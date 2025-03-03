# RL in RL: Reinforcement Learning in Rocket League

## Overview

Welcome to the RL in RL (Reinforcement Learning in Rocket League) project! The primary aim of this project is to train highly skilled bots using reinforcement learning techniques to challenge and ultimately beat Hazem Mansour (my GC1 friend) in Rocket League.

## Frameworks Used

- **RLBot**: This framework allows us to create and control Rocket League bots.
- **RLgym**: A framework designed specifically for training reinforcement learning bots in Rocket League.
- **PPO** (Proximal Policy Optimization): Used as our reinforcement learning algorithm, leveraging hyperparameters and reward systems to optimize bot performance.

## Training Process

The training process was conducted using a separate repository with access to a high-performance GPU. This setup allowed for faster and more efficient training of the `.pt` files (model weights). Once trained, these files can be used on other machines.

## Getting Started

### Requirements

Before you begin, ensure you have met the following requirements:

- Install [Python 3.8](https://www.python.org/downloads/)
- Install RLBot GUI

### Installation

1. **Download RLBot GUI**: Follow the instructions [here](https://www.rlbot.org) to download and install the RLBot GUI.

2. **Download the repository**: Download the repository zip file and extract it.

3. **Load the project in RLBot GUI**: Load the extracted bot into the RLBot GUI using "Load Folder".
   
4. **Download rlgym Library as the RLBot GUI will instruct you**: Click the yellow hazard icon and click install and wait for the terminal to finish installing rlgym. 



## Usage

1. **Load the trained model weights** (already loaded)

   In RLBot GUI, ensure that the trained model weights (`sam-model.pt` files) are correctly loaded.

2. **Start a match**: Use the RLBot GUI to start a match.

3. **Play against SamBotV3**

   Download SamBotV3 and place him in the RLBot directory to challenge the best version of SamBot.

## Main Aim

The main objective of this project is to develop a highly skilled bot that can beat Hazem Mansour in Rocket League. Through the use of RLBot, RLgym, and PPO hyperparameters and reward systems, I've created a challenging and competitive bot.

### Proximal Policy Optimization (PPO)

PPO is a reinforcement learning algorithm designed to improve the training process. It strikes a balance between simplicity, efficiency, and performance. PPO uses a policy gradient method to optimize the agent's actions by adjusting the policy parameters. The main concept behind PPO is to ensure that updates to the policy do not deviate too much from the previous policy, which helps maintain stability during training.

### Reward System

In reinforcement learning, agents learn by interacting with the environment and receiving feedback in the form of rewards. The reward system is crucial in guiding the agent's behavior. Positive rewards encourage desired actions, while negative rewards discourage undesired actions. By designing a well-structured reward system, we can ensure that the agent learns to make decisions that lead to optimal performance in the game.

## Acknowledgment

The initial bot code and example setup were forked from [GoslingUtils](https://github.com/ddthj/GoslingUtils).

