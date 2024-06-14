


import random
import numpy as np
import pickle
import time
from net import PolicyValueNet
from config import CONFIG


class TrainPipeline:

    def __init__(self, init_model=None):
        self.learning_rate = CONFIG['learning_rate']
        self.lr_multiplier = 1.0
        self.temp = 1.0
        self.batch_size = CONFIG['batch_size']
        self.epoch = CONFIG['epoch']
        self.kl_targ = CONFIG['kl_targ']
        self.check_freq = CONFIG['check_freq']
        self.game_batch_num = CONFIG['game_batch_num']

        if init_model:
            try:
                self.policy_value_net = PolicyValueNet(init_model)
                print("Load model successfully")
            except:
                print("Load model failed, use a new model")
                self.policy_value_net = PolicyValueNet()
        else:
            print("Use a new model")
            self.policy_value_net = PolicyValueNet()

    def policy_update(self):
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        state_batch = np.array(state_batch).astype('float32')

        mcts_probs_batch = [data[1] for data in mini_batch]
        mcts_probs_batch = np.array(mcts_probs_batch).astype('float32')

        winner_batch = [data[2] for data in mini_batch]
        winner_batch = np.array(winner_batch).astype('float32')

        old_probs, old_v = self.policy_value_net.policy_value(state_batch)

        for i in range(self.epoch):
            loss, entropy = self.policy_value_net.train_step(state_batch, mcts_probs_batch, winner_batch, self.learning_rate * self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)
            kl = np.mean(np.sum(old_probs * (np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
            if kl > self.kl_targ * 4:# early stopping if D_KL diverges badly
                break

        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 10:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 -
                             np.var(np.array(winner_batch) - old_v.flatten()) /
                             np.var(np.array(winner_batch)))
        explained_var_new = (1 -
                             np.var(np.array(winner_batch) - new_v.flatten()) /
                             np.var(np.array(winner_batch)))

        print(("kl:{:.5f},"
               "lr_multiplier:{:.3f},"
               "loss:{},"
               "entropy:{},"
               "explained_var_old:{:.9f},"
               "explained_var_new:{:.9f}"
               ).format(kl,
                        self.lr_multiplier,
                        loss,
                        entropy,
                        explained_var_old,
                        explained_var_new))
        return loss, entropy

    def run(self):
        try:
            for i in range(self.game_batch_num):
                time.sleep(CONFIG['sleep_time'])
                while True:
                    try:
                        with open(CONFIG['train_data_buffer_path'], 'rb') as f:
                            data_file = pickle.load(f)
                            self.data_buffer = data_file['data_buffer']
                            self.iters = data_file['iters']
                            del data_file
                        print("Data buffer loaded successfully")
                        break
                    except:
                        time.sleep(20)
                print(f'step {self.iters}, buffer length {len(self.data_buffer)}')
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()
                self.policy_value_net.save_model(CONFIG['model_path'])
                if (i + 1) % self.check_freq == 0:
                    print(f"Save model {CONFIG['model_path']} successfully")
                    self.policy_value_net.save_model(f'models/current_policy_batch_{i + 1}.model')
        except KeyboardInterrupt:
            print("KeyboardInterrupt")

if CONFIG['use_frame'] == 'paddle':
    training_pipeline = TrainPipeline(init_model='current_policy.model')
    training_pipeline.run()
elif CONFIG['use_frame'] == 'pytorch':
    training_pipeline = TrainPipeline(init_model='current_policy.pkl')
    training_pipeline.run()
else:
    print('暂不支持您选择的框架')
    print('训练结束')