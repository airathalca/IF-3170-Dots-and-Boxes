from shutil import move
from Bot import Bot
from GameAction import GameAction
from GameState import GameState
import numpy as np
from copy import deepcopy
import random
import time

class MinimaxBot(Bot):
    def __init__(self):
        self.my_turn = True
        self.hit_timeout = False
        self.action = None

    # Mengembalikan aksi yang akan dilakukan
    def get_action(self, state: GameState) -> GameAction:
        self.my_turn = state.player1_turn
        self.hit_timeout = False
        timeout = time.time() + 4
        move_possible = np.count_nonzero(state.row_status == 0) + np.count_nonzero(state.col_status == 0)
        #REVIEW - ini bisa diubah y yg rangenya
        for i in range(1, move_possible + 1):
            if time.time() > timeout:
                break
            temp_action = self.alphabeta(state, i, -np.inf, np.inf, True, timeout)[1]
            if(self.hit_timeout == False and temp_action != None):
                self.action = temp_action
        return GameAction(self.action.action_type, (self.action.position[1], self.action.position[0]))
    
    # Menghitung jumlah poin yang dimiliki oleh player
    def count_point(self, state: GameState, player1: bool) -> int: 
        count = 0
        mult = -1 if player1 else 1
        for i in range (0, state.board_status.shape[0]):
            for j in range (0, state.board_status.shape[1]):
                if state.board_status[i][j] == 4 * mult:
                    count += 1
        return count
    
    # Menghitung nilai state
    def evaluate(self, state: GameState) -> int:
        score = 20*(self.count_point(state, self.my_turn) - self.count_point(state, not self.my_turn))
        if self.is_game_over(state):
            if self.count_point(state, self.my_turn) > self.count_point(state, not self.my_turn):
                score += 1000
            else:
                score -= 1000
        score_config = 0
        for i in range (0, state.board_status.shape[0]):
            for j in range (0, state.board_status.shape[1]):
                if abs(state.board_status[i][j]) == 3:
                    score_config += 10
                elif abs(state.board_status[i][j]) == 2:
                    score_config -= 2
        if (self.my_turn == state.player1_turn):
            score += score_config
        else:
            score -= score_config
        return score
    
    # Mengembalikan semua kemungkinan aksi yang dapat dilakukan
    def get_all_moves(self, state: GameState) -> list:
        all_moves = []
        for i in range (0, state.row_status.shape[0]):
            for j in range (0, state.row_status.shape[1]):
                if state.row_status[i][j] == 0:
                    all_moves.append(GameAction("row", (i, j)))
        for i in range (0, state.col_status.shape[0]):
            for j in range (0, state.col_status.shape[1]):
                if state.col_status[i][j] == 0:
                    all_moves.append(GameAction("col", (i, j)))
        random.shuffle(all_moves)
        return all_moves

    # Mengecek apakah game sudah selesai
    def is_game_over(self, state: GameState) -> bool:
        return (state.row_status == 1).all() and (state.col_status == 1).all()

    # Algoritma minimax dengan alphabeta pruning
    def alphabeta(self, state: GameState, depth=4, alpha= -np.inf, beta= np.inf, agent_turn=True, timeout=5):
        if time.time() > timeout:
            self.hit_timeout = True
            return self.evaluate(state), None
        if depth == 0 or self.is_game_over(state):
            return self.evaluate(state), None
        all_moves = self.get_all_moves(state)
        if agent_turn:
            maxEval = -np.inf
            best_move = all_moves[0]
            best_score = maxEval
            for move in all_moves:
                current = deepcopy(state)
                current = self.apply_action(current, move)
                if(current.player1_turn == state.player1_turn):
                    maxEval = max(maxEval, self.alphabeta(current, depth - 1, alpha, beta, agent_turn, timeout)[0])
                else:
                    maxEval = max(maxEval, self.alphabeta(current, depth - 1, alpha, beta, not agent_turn, timeout)[0])
                if (maxEval > best_score):
                    best_score = maxEval
                    best_move = move
                alpha = max(alpha, maxEval)
                if beta <= alpha:
                    break
            return best_score, best_move

        else:
            minEval = np.inf
            best_move = all_moves[0]
            best_score = minEval
            for move in all_moves:
                current = deepcopy(state)
                current = self.apply_action(current, move)
                if(current.player1_turn == state.player1_turn):
                    minEval = min(minEval, self.alphabeta(current, depth - 1, alpha, beta, agent_turn, timeout)[0])
                else:
                    minEval = min(minEval, self.alphabeta(current, depth - 1, alpha, beta, not agent_turn, timeout)[0])
                if (minEval < best_score):
                    best_score = minEval
                    best_move = move
                beta = min(beta, minEval)
                if beta <= alpha:
                    break
            return best_score, best_move

    # Melakukan aksi pada state
    def apply_action(self, state: GameState, action: GameAction):
        if action.action_type == "row":
            state.row_status[action.position] = 1
        else:
            state.col_status[action.position] = 1
        state = self.check_square(state, action)
        return state
    
    # Mengecek apakah kotak sudah terisi
    def check_square(self, state: GameState, action: GameAction):
        y = action.position[0]
        x = action.position[1]
        change_turn = True
        if state.player1_turn:
            multiplier = -1
        else:
            multiplier = 1
        if y< 3 and x < 3:
            state.board_status[y][x] = (abs(state.board_status[y][x]) + 1) * multiplier
            if abs(state.board_status[y][x]) == 4:
                change_turn = False
        if action.action_type == "row":
            state.row_status[y][x] = 1
            if y >= 1:
                state.board_status[y-1][x] = (abs(state.board_status[y-1][x]) + 1) * multiplier
                if abs(state.board_status[y-1][x]) == 4:
                    change_turn = False
        elif action.action_type == 'col':
            state.col_status[y][x] = 1
            if x >= 1:
                state.board_status[y][x-1] = (abs(state.board_status[y][x-1]) + 1) * multiplier
                if abs(state.board_status[y][x-1]) == 4:
                    change_turn = False
        if change_turn:
            state = state._replace(player1_turn = not state.player1_turn)
        return state
