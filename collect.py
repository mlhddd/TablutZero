

from collections import deque
import copy
import os
import pickle
import time
import numpy as np
from chess import Board, Game, move_id2move_action, move_action2move_id, flip_map_x, flip_map_y
from net import PolicyValueNet
from mcts import MCTSPlayer
from config import CONFIG


class CollectPipeline:

    def __init__(self, init_model = None, use_gpu=True, device='cuda'):
        self.board = Board()
        self.game = Game(self.board)
        self.temp = 1
        self.n_playout = CONFIG['n_playout']
        self.c_puct = CONFIG['c_puct']
        self.buffer_size = CONFIG['buffer_size']
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.iters = 0

    def load_model(self, model_path = CONFIG['model_path']):
        try:
            self.policy_value_net = PolicyValueNet(model_path)
            print("Load model successfully")
        except:
            self.policy_value_net = PolicyValueNet()
            print("Load model failed, use a new model")
        self.mcst_player = MCTSPlayer(self.policy_value_net.policy_value_fn, self.c_puct, self.n_playout, is_selfplay = 1)

    def get_equi_data_x(self, play_data):
        extend_data = []
        for state, mcts_prob, winner in play_data:
            extend_data.append((state, mcts_prob, winner))
            state_flip = state.transpose([1, 2, 0])
            state = state.transpose([1, 2, 0])
            for i in range(9):
                for j in range(9):
                    state_flip[i][j] = state[i][8 - j]
            state_flip = state_flip.transpose([2, 0, 1])
            mcts_prob_flip = copy.deepcopy(mcts_prob)
            for i in range(len(mcts_prob_flip)):
                mcts_prob_flip[i] = mcts_prob[move_action2move_id[flip_map_x(move_id2move_action[i])]]
            extend_data.append((state_flip, mcts_prob_flip, winner))
        return extend_data

    def get_equi_data_y(self, play_data):
        extend_data = []
        for state, mcts_prob, winner in play_data:
            extend_data.append((state, mcts_prob, winner))
            state_flip = state.transpose([1, 2, 0])
            state = state.transpose([1, 2, 0])
            for i in range(9):
                for j in range(9):
                    state_flip[i][j] = state[8 - i][j]
            state_flip = state_flip.transpose([2, 0, 1])
            mcts_prob_flip = copy.deepcopy(mcts_prob)
            for i in range(len(mcts_prob_flip)):
                mcts_prob_flip[i] = mcts_prob[move_action2move_id[flip_map_y(move_id2move_action[i])]]
            extend_data.append((state_flip, mcts_prob_flip, winner))
        return extend_data

    def collect_selfplay_data(self, n_games=1):
        for i in range(n_games):
            self.load_model()
            winner, play_data = self.game.start_self_play(self.mcst_player, temp=self.temp, is_shown=False)
            print(f' winner is {winner}')
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            # augment the data
            play_data = self.get_equi_data_x(play_data)
            play_data = self.get_equi_data_y(play_data)
            if os.path.exists(CONFIG['train_data_buffer_path']):
                while True:
                    try:
                        with open(CONFIG['train_data_buffer_path'], 'rb') as f:
                            data_file = pickle.load(f)
                            self.data_buffer = data_file['data_buffer']
                            self.iters = data_file['iters']
                            del data_file
                            self.iters += 1
                            self.data_buffer.extend(play_data)
                        print("Data buffer loaded successfully")
                        break
                    except:
                        time.sleep(20)
            else:
                self.data_buffer.extend(play_data)
                self.iters += 1
            f = {'data_buffer': self.data_buffer, 'iters': self.iters}
            with open(CONFIG['train_data_buffer_path'], 'wb') as file:
                pickle.dump(f, file)
        return  self.iters

    def run(self):
        try:
            while True:
                self.collect_selfplay_data()
                print(f'batch {self.iters}, episode_len:{self.episode_len}')

        except KeyboardInterrupt:
            print('\n\rquit')

collecting_pipeline = CollectPipeline(init_model='current_policy.pkl')
collecting_pipeline.run()

if CONFIG['use_frame'] == 'paddle':
    collecting_pipeline = CollectPipeline(init_model='current_policy.model')
    collecting_pipeline.run()
elif CONFIG['use_frame'] == 'pytorch':
    collecting_pipeline = CollectPipeline(init_model='current_policy.pkl')
    collecting_pipeline.run()
else:
    print('暂不支持您选择的框架')
    print('训练结束')