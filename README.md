# TablutZero

TablutZero is a machine learning project that utilizes the AlphaZero algorithm to master the Nordic traditional board game, Tablut. This project combines reinforcement learning with Monte Carlo Tree Search (MCTS) and deep neural networks to create an AI capable of self-play and strategy optimization. The project is the final project in the Machine Learning in the Tsinghua University, which is taught by the professor Mingsheng Long.

## Features

- **Reinforcement Learning**: Self-play learning using the AlphaZero framework.
- **Monte Carlo Tree Search (MCTS)**: Integrates neural networks to optimize decision-making in the search tree.
- **Neural Networks**: Employs convolutional and residual networks to analyze board states and predict moves.

## How to train the model
You can run the code below repeatly to get the enough chess data in a shorter time, which may be constrained by the GPU of your computer. Make sure that you have configured the PyTorch environment.
```bash
cd TablutZero
python collect.py
```
After you run the code above, you need to run the code below at the same time to train the model.
```bash
python train.py
```
## How to play with the model that you have trained
The models that you have trained are stored in the dictionary. You can run the UIplay.py to play with the model trained by you or let your models to play with each other, and you can choose the model that you want to play with.

## References
- https://github.com/tensorfly-gpu/aichess I use the frame of this project.
- https://www.bilibili.com/video/BV183411g7GX
- Mastering the game of Go with deep neural networks and tree search
- Mastering the game of Go without human knowledge
- Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
