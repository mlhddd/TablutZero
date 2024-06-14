"control the chess game"
import numpy as np
import copy
import time
from config import CONFIG
from collections import deque
import random


#棋盘如下：红方为进攻方，黑方为防守方，使用时需要深拷贝
state_list_init = [['---', '---', '---', 'red', 'red', 'red', '---', '---', '---'],
                   ['---', '---', '---', '---', 'red', '---', '---', '---', '---'],
                   ['---', '---', '---', '---', 'bla', '---', '---', '---', '---'],
                   ['red', '---', '---', '---', 'bla', '---', '---', '---', 'red'],
                   ['red', 'red', 'bla', 'bla', 'kin', 'bla', 'bla', 'red', 'red'],
                   ['red', '---', '---', '---', 'bla', '---', '---', '---', 'red'],
                   ['---', '---', '---', '---', 'bla', '---', '---', '---', '---'],
                   ['---', '---', '---', '---', 'red', '---', '---', '---', '---'],
                   ['---', '---', '---', 'red', 'red', 'red', '---', '---', '---']]


state_deque_init = deque(maxlen=4)
for i in range(4):
    state_deque_init.append(copy.deepcopy(state_list_init))

string2array = {'red': np.array([1, 0, 0]),
                'bla': np.array([0, 1, 0]),
                'kin': np.array([0, 0, 1]),
                '---': np.array([0, 0, 0])}

def array2string (array):
    return list(filter(lambda string:(string2array[string]==array).all(), string2array))[0]

def checkstate(copy_list):
    if copy_list[4][4] == '---':
        copy_list[4][4] = 'cas'
    for y in [0, 8]:
        for x in [3, 4, 5]:
            if copy_list[y][x] == '---':
                copy_list[y][x] = 'cam'
    for x in [0, 8]:
        for y in [3, 4, 5]:
            if copy_list[y][x] == '---':
                copy_list[y][x] = 'cam'
    if copy_list[1][4] == '---':
        copy_list[1][4] = 'cam'
    if copy_list[4][1] == '---':
        copy_list[4][1] = 'cam'
    if copy_list[4][7] == '---':
        copy_list[4][7] = 'cam'
    if copy_list[7][4] == '---':
        copy_list[7][4] = 'cam'
    return copy_list
def deletestate(copy_list):
    if copy_list[4][4] == 'cas':
        copy_list[4][4] = '---'
    for y in [0, 8]:
        for x in [3, 4, 5]:
            if copy_list[y][x] == 'cam':
                copy_list[y][x] = '---'
    for x in [0, 8]:
        for y in [3, 4, 5]:
            if copy_list[y][x] == 'cam':
                copy_list[y][x] = '---'
    if copy_list[1][4] == 'cam':
        copy_list[1][4] = '---'
    if copy_list[4][1] == 'cam':
        copy_list[4][1] = '---'
    if copy_list[4][7] == 'cam':
        copy_list[4][7] = '---'
    if copy_list[7][4] == 'cam':
        copy_list[7][4] = '---'
    return copy_list


def change_state(state_list, move):
    """move:string '0313' means move from (1,4) to (2,4)
    state_list: chess board"""
    copy_list=copy.deepcopy(state_list)
    y,x,to_y,to_x=int(move[0]),int(move[1]),int(move[2]),int(move[3])
    copy_list[to_y][to_x]=copy_list[y][x]
    copy_list[y][x]='---'
    return copy_list

def print_board(state_array):
    """state_array: 9*9*3"""
    camp_list_1 = [(0, 3), (0, 4), (0, 5), (1, 4)]
    camp_list_2 = [(8, 3), (8, 4), (8, 5), (7, 4)]
    camp_list_3 = [(3, 0), (4, 0), (5, 0), (4, 1)]
    camp_list_4 = [(3, 8), (4, 8), (5, 8), (4, 7)]
    camp_list = camp_list_1 + camp_list_2 + camp_list_3 + camp_list_4
    for i in range(9):
        boardline=[]
        for j in range(9):
            if i == 4 and j == 4 and array2string(state_array[i][j]) == '---':
                boardline.append('cas')
            elif (i, j) in camp_list and array2string(state_array[i][j]) == '---':
                boardline.append('cam')
            else:
                boardline.append(array2string(state_array[i][j]))
        print(boardline)

def state_list2state_array(state_list):
    """state_list: 9*9"""
    state_array=np.zeros((9,9,3))
    for i in range(9):
        for j in range(9):
            state_array[i][j]=string2array[state_list[i][j]]
    return state_array

def get_all_legal_move():
    move_id2move_action={}
    move_action2move_id={}
    idx=0
    for i in range(9):
        for j in range(9):
            destination=[(i, t) for t in range(9)]+[(t, j) for t in range(9)]
            for (a, b) in destination:
                if (a, b)!=(i, j) and (a, b) != (4, 4):
                    action = str(i) + str(j) + str(a) + str(b)
                    move_id2move_action[idx]=action
                    move_action2move_id[action]=idx
                    idx+=1
    return move_id2move_action, move_action2move_id
move_id2move_action, move_action2move_id=get_all_legal_move()

def flip_map_x(string):
    new_str = ''
    for index in range(4):
        if index == 0 or index == 2:
            new_str += (str(string[index]))
        else:
            new_str += (str(8 - int(string[index])))
    return new_str

def flip_map_y(string):
    new_str = ''
    for index in range(4):
        if index == 1 or index == 3:
            new_str += (str(string[index]))
        else:
            new_str += (str(8 - int(string[index])))
    return new_str


def get_legal_moves(state_deque, player_color):
    """state_list: 9*9
    player: 'red' or 'bla'"""
    if player_color =='red':
        pieces=['red']
    else:
        pieces=['bla', 'kin']
    legal_moves=[]
    state_list = state_deque[-1]
    old_state_list = state_deque[-4]
    camp_list_1 = [(0, 3), (0, 4), (0, 5), (1, 4)]
    camp_list_2 = [(8, 3), (8, 4), (8, 5), (7, 4)]
    camp_list_3 = [(3, 0), (4, 0), (5, 0), (4, 1)]
    camp_list_4 = [(3, 8), (4, 8), (5, 8), (4, 7)]
    camp_list = camp_list_1 + camp_list_2 + camp_list_3 + camp_list_4
    def in_other_camp(y, x, to_y, to_x):
        if (y, x) in camp_list_1 and (to_y, to_x) in camp_list:
            return True
        if (y, x) in camp_list_2 and (to_y, to_x) in camp_list_2:
            return True
        if (y, x) in camp_list_3 and (to_y, to_x) in camp_list_3:
            return True
        if (y, x) in camp_list_4 and (to_y, to_x) in camp_list_4:
            return True
        return False
    for y in range(9):
        for x in range(9):
            if state_list[y][x] in pieces:
                to_y = y
                for to_x in range(x - 1, -1, -1):
                    same_camp_condition = (((y, x) in camp_list_1 and (to_y, to_x) in camp_list_1)
                                           or ((y, x) in camp_list_2 and (to_y, to_x) in camp_list_2)
                                           or ((y, x) in camp_list_3 and (to_y, to_x) in camp_list_3)
                                           or ((y, x) in camp_list_4 and (to_y, to_x) in camp_list_4)
                                            or (to_y, to_x) not in camp_list)
                    if state_list[to_y][to_x] != '---' or not same_camp_condition or (to_y, to_x) == (4, 4):
                        break
                    else:
                        move = str(y) + str(x) + str(to_y) + str(to_x)
                        if change_state(state_list, move) != old_state_list:
                            legal_moves.append(move)
                for to_x in range(x + 1, 9):
                    same_camp_condition = (((y, x) in camp_list_1 and (to_y, to_x) in camp_list_1)
                                           or ((y, x) in camp_list_2 and (to_y, to_x) in camp_list_2)
                                           or ((y, x) in camp_list_3 and (to_y, to_x) in camp_list_3)
                                           or ((y, x) in camp_list_4 and (to_y, to_x) in camp_list_4)
                                           or (to_y, to_x) not in camp_list)
                    if state_list[to_y][to_x] != '---' or not same_camp_condition or (to_y, to_x) == (4, 4):
                        break
                    else:
                        move = str(y) + str(x) + str(to_y) + str(to_x)
                        if change_state(state_list, move) != old_state_list:
                            legal_moves.append(move)
                to_x = x
                for to_y in range(y - 1, -1, -1):
                    same_camp_condition = (((y, x) in camp_list_1 and (to_y, to_x) in camp_list_1)
                                           or ((y, x) in camp_list_2 and (to_y, to_x) in camp_list_2)
                                           or ((y, x) in camp_list_3 and (to_y, to_x) in camp_list_3)
                                           or ((y, x) in camp_list_4 and (to_y, to_x) in camp_list_4)
                                           or (to_y, to_x) not in camp_list)
                    if state_list[to_y][to_x] != '---' or not same_camp_condition or (to_y, to_x) == (4, 4):
                        break
                    else:
                        move = str(y) + str(x) + str(to_y) + str(to_x)
                        if change_state(state_list, move) != old_state_list:
                            legal_moves.append(move)
                for to_y in range(y + 1, 9):
                    same_camp_condition = (((y, x) in camp_list_1 and (to_y, to_x) in camp_list_1)
                                           or ((y, x) in camp_list_2 and (to_y, to_x) in camp_list_2)
                                           or ((y, x) in camp_list_3 and (to_y, to_x) in camp_list_3)
                                           or ((y, x) in camp_list_4 and (to_y, to_x) in camp_list_4)
                                           or (to_y, to_x) not in camp_list)
                    if state_list[to_y][to_x] != '---' or not same_camp_condition or (to_y, to_x) == (4, 4):
                        break
                    else:
                        move = str(y) + str(x) + str(to_y) + str(to_x)
                        if change_state(state_list, move) != old_state_list:
                            legal_moves.append(move)


    moves_id = [move_action2move_id[move] for move in legal_moves]
    return moves_id

def check_victory(direction, start, end, step, state_list, x, y):
    for i in range(start, end, step):
        if (direction == 'vertical' and state_list[i][x] != "---") or (direction == 'horizontal' and state_list[y][i] != "---"):
            return False
    return True

class Board(object):

    def __init__(self):
        self.state_list = copy.deepcopy(state_list_init)
        self.game_start = False
        self.winner = None
        self.state_deque = copy.deepcopy(state_deque_init)

    def init_board(self, start_player = 0):
        #define the color of the player
        self.id2color = {0: 'red', 1: 'bla'}
        self.color2id = {'red': 0, 'bla': 1}
        self.piece2id = {'red': 0, 'bla': 1, 'kin': 1}
        #define the current player
        self.current_player_color = self.id2color[start_player]
        self.current_player_id = start_player
        #initialize the state_list and state_deque
        self.state_list = copy.deepcopy(state_list_init)
        self.state_deque = copy.deepcopy(state_deque_init)
        #initialize the game_start and winner
        self.last_move = -1
        self.kill_action = 0
        self.game_start = False
        self.action_count = 0
        self.winner = None

    def whether_kill(self, state_list, move_action, current_player_id):
        kill_list = []
        kill = False
        y, x, to_y, to_x = map(int, move_action)
        state_list = checkstate(state_list)

        if current_player_id == 0:
            opponent_kill_list = ['bla', 'kin']
            opponent_list = ['bla', 'kin', 'cas']
            current_list = ['red', 'cam']
        else:
            opponent_kill_list = ['red']
            opponent_list = ['red', 'cam']
            current_list = ['bla', 'kin', 'cas']

        check_positions = {(3, 4): (2, 4), (4, 3): (4, 2), (4, 5): (4, 6), (5, 4): (6, 4)}

        # 要检查的方向：(delta_y, delta_x)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        def check_kill(to_y, to_x, d_y, d_x):
            nonlocal kill
            pos_y, pos_x = to_y + 2*d_y, to_x + 2*d_x
            kill_y, kill_x = to_y + d_y, to_x + d_x
            camp_head_list = [(1, 4), (4, 1), (4, 7), (7, 4)]
            if 0 <= pos_y <= 8 and 0 <= pos_x <= 8 and (kill_y, kill_x) not in camp_head_list and (kill_y, kill_x) != (4, 4):
                if state_list[pos_y][pos_x] in current_list and state_list[kill_y][kill_x] in opponent_kill_list:
                    special_condition = state_list[kill_y][kill_x] == 'kin' and (kill_y, kill_x) in check_positions
                    if special_condition:
                        target_y, target_x = check_positions[(kill_y, kill_x)]
                        if state_list[target_y][target_x] in current_list:
                            kill_list.append('kin')
                            state_list[kill_y][kill_x] = '---'
                            kill = True
                    elif state_list[kill_y][kill_x] == 'kin' and (kill_y, kill_x) is (4, 4):
                        if state_list[4][3] == 'red' and state_list[4][5] == 'red' and state_list[3][4] == 'red' and state_list[5][4] == 'red':
                            kill_list.append('kin')
                            state_list[kill_y][kill_x] = '---'
                            kill = True
                    else:
                        kill_list.append(state_list[kill_y][kill_x])
                        state_list[kill_y][kill_x] = '---'
                        if state_list[4][4] == '---':
                            state_list[4][4] = 'cas'
                        for y in [0, 8]:
                            for x in [3, 4, 5]:
                                if state_list[y][x] == '---':
                                    state_list[y][x] = 'cam'
                        for x in [0, 8]:
                            for y in [3, 4, 5]:
                                if state_list[y][x] == '---':
                                    state_list[y][x] = 'cam'
                        kill = True
                elif current_player_id == 0 and state_list[pos_y][pos_x] == 'cas':
                    if state_list[kill_y + d_x][kill_x + d_y] == 'red' and state_list[kill_y - d_x][kill_x - d_y] == 'red':
                        kill_list.append('kin')
                        state_list[pos_y][pos_x] = '---'
                        kill = True
            elif (kill_y, kill_x) == (4, 4) and state_list[4][5] == 'red' and state_list[4][3] == 'red' and state_list[3][4] == 'red' and state_list[5][4] == 'red':
                kill_list.append('kin')
                kill = True

        for dy, dx in directions:
            check_kill(to_y, to_x, dy, dx)

        if kill:
            self.kill_action = 0
        else:
            self.kill_action += 1
        state_list = deletestate(state_list)
        return state_list, kill, kill_list

    @property
    #get all the legal actions
    def available_actions(self):
        return get_legal_moves(self.state_deque, self.current_player_color)

    def current_state(self):
        current_state = np.zeros([5, 9, 9])
        # return the state_array, which is 5*9*9
        if self.game_start:
            #get the current state, which is 3*9*9
            current_state[:3] = state_list2state_array(self.state_deque[-1]).transpose([2, 0, 1])
            move = move_id2move_action[self.last_move]
            current_state[3][int(move[0])][int(move[1])] = -1
            current_state[3][int(move[2])][int(move[3])] = 1
        #point out the current player
        if self.current_player_color == 'red':
            current_state[4] = np.ones([9, 9])
        else:
            current_state[4] = np.zeros([9, 9])
        return current_state


    def check_winner(self, x_kin, y_kin, state_list):
        # Vertical upwards
        if check_victory('vertical', y_kin - 1, -1, -1, state_list, x_kin, y_kin):
            self.winner = 1
        # Vertical downwards
        if check_victory('vertical', y_kin + 1, 8, 1, state_list, x_kin, y_kin):
            self.winner = 1
        # Horizontal left
        if check_victory('horizontal', x_kin - 1, -1, -1, state_list, x_kin, y_kin):
            self.winner = 1
        # Horizontal right
        if check_victory('horizontal', x_kin + 1, 8, 1, state_list, x_kin, y_kin):
            self.winner = 1

    def do_move(self, move):
        #change the state_list and state_deque
        self.game_start = True
        self.action_count += 1
        move_action = move_id2move_action[move]
        start_y, start_x = int(move_action[0]), int(move_action[1])
        end_y, end_x = int(move_action[2]), int(move_action[3])
        state_list = copy.deepcopy(self.state_deque[-1])
        #change the state of board
        state_list = change_state(state_list, move_action)
        #jusge whether there is a kill action
        state_list, kill, kill_list = self.whether_kill(state_list, move_action, self.current_player_id)
        if "kin" in kill_list:
            self.winner = 0
        if self.current_player_id == 1:
            for i in range(len(state_list)):
                for j in range(len(state_list[i])):
                    if state_list[i][j] == "kin":
                        y_kin = i
                        x_kin = j
                        if y_kin == 0 or y_kin == 8 or x_kin == 0 or x_kin == 8:
                            self.winner = 1



        #change the current player
        self.current_player_color = 'red' if self.current_player_color == 'bla' else 'bla'
        self.current_player_id = 1 - self.current_player_id
        self.last_move = move
        self.state_deque.append(state_list)

    @property
    def has_a_winner(self):
        if self.winner is not None:
            return True, self.winner
        elif self.kill_action >= CONFIG['kill_action']:
            return False, -1
        return False, -1

    def game_end(self):
        win, winner = self.has_a_winner
        if win:
            return True, winner
        elif self.kill_action >= CONFIG['kill_action']:
            return True, -1
        return False, -1

    def get_current_player_color(self):
        return self.current_player_color

    def get_current_player_id(self):
        return self.current_player_id


class Game(object):

    def __init__(self, board):
        self.board = board


    #visualize
    def graphic(self, board, player1_color, player2_color):
        print('player1 takes:', player1_color)
        print('player2 takes:', player2_color)
        print_board(state_list2state_array(self.board.state_deque[-1]))

    #human vs AI OR AI vs AI OR human vs human
    def start_play(self, player1, player2, start_player = 0, is_shown = 1):
        if start_player not in (0, 1):
            raise Exception('start_player should be 0 or 1')
        self.board.init_board(start_player)
        player1.set_player_ind(0)
        player2.set_player_ind(1)
        players = {0: player1, 1: player2}
        if is_shown:
            self.graphic(self.board, player1.player, player2.player)
        while True:
            while True:
                player_in_turn = players[self.board.get_current_player_id()]
                move = player_in_turn.get_action(self.board)
                if move in get_legal_moves(self.board.state_deque, self.board.current_player_color):
                    self.board.do_move(move)
                    break
                else:
                    print('invalid move')
            if is_shown:
                self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if winner != -1:
                    print('Game end. Winner is', players[winner])
                else:
                    print('Game end. Tie')
                return winner
    #use Monte Carlo Tree Search to play, retore the result
    def start_self_play(self, player, is_shown = 1, temp = 1e-3):
        self.board.init_board()
        states, mcts_probs, current_players = [], [], []
        #start the game
        _count = 0
        while True:
            _count += 1
            if _count % 20 == 0:
                start_time = time.time()
                move, move_probs = player.get_action(self.board, temp = temp, return_prob = 1)
                print('play round', time.time() - start_time)
            else:
                move, move_probs = player.get_action(self.board, temp = temp, return_prob = 1)
            #store the data
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player_id)
            #perform the move
            self.board.do_move(move)
            end, winner = self.board.game_end()
            if end:
                #store the result
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print('Game end. Winner is', winner)
                    else:
                        print('Game end. Tie')

                return winner, zip(states, mcts_probs, winners_z)


if __name__ == '__main__':
    # #test change_state
    # new_state = change_state(state_list_init, move='0313')
    #
    #
    # #test print_board
    # state_list=copy.deepcopy(state_list_init)
    # print_board(state_list2state_array(state_list))
    #
    # #test get_all_legal_move
    # print(move_id2move_action)
    #
    # test get_legal_moves
    # moves = get_legal_moves(state_deque_init, 'red')
    # moves_action=[]
    # for item in moves:
    #     moves_action.append(move_id2move_action[item])
    # print(moves_action)
    # print(len(moves))
    # 测试Board中的start_play
    # class Human1:
    #     def get_action(self, board):
    #         # print('当前是player1在操作')
    #         # print(board.current_player_color)
    #         # move = move_action2move_id[input('请输入')]
    #         move = random.choice(board.available_actions)
    #         return move
    #
    #     def set_player_ind(self, p):
    #         self.player = p
    #
    #
    # class Human2:
    #     def get_action(self, board):
    #         # print('当前是player2在操作')
    #         # print(board.current_player_color)
    #         # move = move_action2move_id[input('请输入')]
    #         move = random.choice(board.available_actions)
    #         return move
    #
    #     def set_player_ind(self, p):
    #         self.player = p
    #
    # human1 = Human1()
    # human2 = Human2()
    # game = Game(board=Board())
    # for i in range(1):
    #     game.start_play(human1, human2, start_player=0, is_shown=0)
    #     print(game.start_self_play(human1, human2, start_player=0, is_shown=0))
    board = Board()
    board.init_board()