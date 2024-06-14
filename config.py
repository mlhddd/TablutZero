CONFIG={
    'kill_action': 40,
    'n_playout': 500,
    'dirichlet': 0.3, #chinese chess 0.3, chess 0.15, Go 0.03
    'c_puct': 5, #
    'buffer_size': 50000, #
    'model_path': 'current_policy.pkl', #model path
    'train_data_buffer_path': 'train_data_buffer.pkl',#data buffer path
    'learning_rate': 1e-3, #learning rate
    'batch_size': 512, #the number of data in each batch
    'epoch': 5, #the number of epoch in each train
    'kl_targ': 0.02, #KL divergence
    'check_freq': 10, #the frequency of check
    'game_batch_num': 10000, #the number of game in each batch
    'use_frame' : 'pytorch', #use pytorch or paddle
    'sleep_time': 240 #sleep time

}