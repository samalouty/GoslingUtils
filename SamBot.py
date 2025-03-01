from tools import *
from objects import *
from routines import *


class SamBot(GoslingAgent):
    def run(agent):
        # Main game logic
        if len(agent.stack) < 1:
            if agent.kickoff_flag:
                agent.push(kickoff())
            else:
                # Get ball prediction
                ball_prediction = agent.get_ball_prediction_struct()

                # Find shots we can take
                shots = find_shots(agent, ball_prediction)

                # Boost management and collection
                if should_collect_boost(agent):
                    closest_boost = find_closest_boost(agent)
                    if closest_boost is not None:
                        # Pass target to boost routine to optimize path after boost
                        if len(shots) > 0:
                            agent.push(goto_boost(closest_boost, shots[0].ball_location))
                        else:
                            agent.push(goto_boost(closest_boost))
                        return

                # If we have shots, take them
                if len(shots) > 0:
                    # Sort shots by how promising they are
                    shots.sort(key=lambda shot: shot_quality(agent, shot))
                    best_shot = shots[0]
                    agent.push(best_shot)
                    return

                # If we can't shoot, decide what to do based on game state
                if defensive_positioning_needed(agent):
                    target_pos = defensive_position(agent)
                    agent.push(goto(target_pos, agent.foe_goal.location - agent.me.location))
                else:
                    # Get in position for a shot
                    target_pos = offensive_position(agent)
                    agent.push(goto(target_pos, agent.ball.location - agent.me.location))

                    # If we're close to the ball but don't have a good shot yet, try to hit it anyway
                    if (agent.me.location - agent.ball.location).magnitude() < 500:
                        agent.push(short_shot(agent.foe_goal.location))


def should_collect_boost(agent):
    """Determine if we should go for boost"""
    # Don't go for boost if we already have enough
    if agent.me.boost > 50:
        return False

    # Don't go for boost if we're the closest to the ball and it's close to our goal
    if (agent.me.location - agent.ball.location).magnitude() < 1500:
        if (agent.ball.location - agent.friend_goal.location).magnitude() < 3500:
            return False

    # Don't go for boost if we're airborne
    if agent.me.airborne:
        return False

    # Go for boost if we're low and it's safe
    return agent.me.boost < 30


def find_shots(agent, ball_prediction):
    """Find possible shots to take based on ball prediction"""
    shots = []

    # Ground and jump shot checks
    for i in range(10, 60):
        # Look at predictions 0.1s to 3.0s in the future
        i *= 6  # Always make sure indexes align with the prediction struct

        # Get the prediction at this time
        pred = ball_prediction.slices[i]
        ball_location = Vector3(pred.physics.location.x, pred.physics.location.y, pred.physics.location.z)
        time = pred.game_seconds - agent.time

        # Check if ball is still in valid shot range
        if abs(ball_location[1]) > 5120:  # Skip if ball is behind a goal
            continue

        # Check if we could reach this ball with a jump shot
        if ball_location[2] < 300:
            # Calculate shot vectors (towards enemy goal)
            shot_vector = (agent.foe_goal.location - ball_location).normalize()

            # Calculate car to ball vector to see how we're aligned
            car_to_ball = (ball_location - agent.me.location).normalize()

            # Alignment with shot (dot product)
            alignment = car_to_ball.dot(shot_vector)

            # If we're somewhat aligned, consider the shot
            if alignment > 0.5:
                shots.append(jump_shot(ball_location, agent.time + time, shot_vector, alignment,
                                       direction=determine_approach_direction(agent, ball_location)))

        # Check for aerial shots when ball is higher (if we have boost)
        elif ball_location[2] > 300 and ball_location[2] < 750 and agent.me.boost > 30:
            # Calculate shot vectors (towards enemy goal)
            shot_vector = (agent.foe_goal.location - ball_location).normalize()

            # Calculate car to ball vector to see how we're aligned
            car_to_ball = (ball_location - agent.me.location).normalize()

            # Alignment with shot (dot product)
            alignment = car_to_ball.dot(shot_vector)

            # If we're somewhat aligned, consider the shot
            if alignment > 0.7:  # Higher standard for aerials
                shots.append(aerial_shot(ball_location, agent.time + time, shot_vector, alignment))

    # Also consider immediate shots if the ball is close
    if (agent.me.location - agent.ball.location).magnitude() < 1500 and agent.ball.location[2] < 300:
        shot_vector = (agent.foe_goal.location - agent.ball.location).normalize()
        car_to_ball = (agent.ball.location - agent.me.location).normalize()
        alignment = car_to_ball.dot(shot_vector)

        if alignment > 0.3:  # Lower threshold for immediate shots
            shots.append(short_shot(agent.foe_goal.location))

    # Filter shots by whether they're valid
    valid_shots = []
    for shot in shots:
        if hasattr(shot, 'ball_location') and shot_valid(agent, shot):
            valid_shots.append(shot)

    return valid_shots


def determine_approach_direction(agent, ball_location):
    """Determine the best direction to approach the ball from (forward or backward)"""
    car_to_ball = ball_location - agent.me.location
    car_to_ball_direction = car_to_ball.normalize()

    # Check the angle between where the car is facing and where the ball is
    forward_direction = agent.me.forward.normalize()
    angle = forward_direction.angle(car_to_ball_direction)

    # If the angle is too wide, it might be better to go backward
    if angle > 2.8:  # About 160 degrees
        return -1  # Backward

    return 1  # Forward


def shot_quality(agent, shot):
    """Rate a shot's quality based on different factors"""
    # Handle short_shot which doesn't have these attributes
    if not hasattr(shot, 'ball_location'):
        return -10  # Lower priority for short shots

    # Distance to the ball (closer is better)
    ball_dist = (agent.me.location - shot.ball_location).magnitude()

    # Time until interception (sooner is better)
    time_factor = shot.intercept_time - agent.time

    # How centered the shot is on the goal
    goal_center = agent.foe_goal.location
    shot_on_target = 1.0 - (abs(shot.ball_location[0] - goal_center[0]) / 800)

    # Speed check - prioritize shots we can reach at max speed
    speed_factor = 0
    time_to_ball = time_factor
    distance_possible = 2300 * time_to_ball  # Max speed * time

    if distance_possible >= ball_dist:
        speed_factor = 1.5  # Bonus for shots we can reach at full speed

    # Combine factors (weighted)
    quality = shot.ratio * 2.0  # Shot alignment is important
    quality -= time_factor * 0.5  # Sooner is better
    quality += shot_on_target * 1.5  # On target is important
    quality -= ball_dist / 10000  # Distance matters less
    quality += speed_factor  # Speed bonus

    return quality


def find_closest_boost(agent):
    """Find the closest available boost"""
    closest_boost = None
    closest_distance = float('inf')

    for boost in agent.boosts:
        if boost.active and not agent.me.airborne:
            dist = (agent.me.location - boost.location).magnitude()
            if dist < closest_distance:
                closest_distance = dist
                closest_boost = boost

    return closest_boost


def defensive_positioning_needed(agent):
    """Determine if we need to position defensively"""
    ball_to_our_goal = (agent.friend_goal.location - agent.ball.location).magnitude()
    ball_to_their_goal = (agent.foe_goal.location - agent.ball.location).magnitude()

    # If ball is closer to our goal than theirs
    if ball_to_our_goal < ball_to_their_goal:
        return True

    # If ball is moving toward our goal fast
    ball_velocity = agent.ball.velocity
    goal_direction = (agent.friend_goal.location - agent.ball.location).normalize()
    velocity_toward_goal = ball_velocity.dot(goal_direction)

    if velocity_toward_goal > 500:
        return True

    return False


def defensive_position(agent):
    """Calculate a good defensive position"""
    ball_loc = agent.ball.location
    goal_loc = agent.friend_goal.location

    # Position between ball and goal, closer to goal
    goal_to_ball = (ball_loc - goal_loc).normalize()
    distance_from_goal = min(1000, (ball_loc - goal_loc).magnitude() * 0.5)
    target_pos = goal_loc + (goal_to_ball * distance_from_goal)

    # Don't position too far to the sides
    target_pos[0] = cap(target_pos[0], -800, 800)

    return target_pos


def offensive_position(agent):
    """Calculate a good offensive position"""
    ball_loc = agent.ball.location
    goal_loc = agent.foe_goal.location

    # Position between ball and goal, closer to ball
    ball_to_goal = (goal_loc - ball_loc).normalize()
    target_pos = ball_loc + (ball_to_goal * -1000)  # 1000 units behind the ball toward enemy goal

    # Make sure we're not too far to the sides
    target_pos[0] = cap(target_pos[0], -3000, 3000)
    target_pos[1] = cap(target_pos[1], -4000, 4000)

    return target_pos