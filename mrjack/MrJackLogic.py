import numpy as np
import random
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self, board = None):
        "Set up initial board configuration."

        if board is None:
            self.currentPlayer = 1  # Detective
            self.round = 0
            self.witness = 1 # Visible
            self.jack = random.randint(1, 8)
            self.visible = np.array([0,1] * 4)
            self.innocent = np.zeros(8, int)
            self.cards = np.arange(1, 9)
            np.random.shuffle(self.cards)
        else:
            self.currentPlayer = board[0]
            self.round = board[1]
            self.witness = board[2]
            self.jack = board[3]
            self.visible = np.copy(board[4:12])
            self.innocent = np.copy(board[12:20])
            self.cards = np.trim_zeros(board[20:28])

    def get_legal_moves(self):
        if self.game_ended(self.currentPlayer) != 0:
            return []
        
        initPos = 0 if len(self.cards) <= 4 else 4

        # return every available card in the subgroup of 4 cards
        moves = [(int(self.cards[initPos + i]),j) for i in range(len(self.cards) - initPos) for j in range(0,2)]
        return moves

    def execute_move(self, move):
        #        print(f"cards: {len(self.c
# ards)}, flag: {len(self.cards) % 4}" )

        character = move[0]
        visible = move[1]

        assert character >= 1 and character <= 8 and visible >= 0 and visible <= 1

        self.cards = np.delete(self.cards, np.where(self.cards == character))
        self.visible[character - 1] = visible


        if (len(self.cards)%4 == 0):
            self.witness = self.visible[self.jack - 1]
            self.innocent = np.array([self.innocent[i] or int(self.visible[i] != self.witness) for i in range(8)])
            self.round += 1

            if len(self.cards) == 0 and self.round < 7:
                self.cards = np.arange(1, 9)
                np.random.shuffle(self.cards)

        if len(self.cards) % 4 != 2:
            self.currentPlayer = -self.currentPlayer
        

    def game_ended(self, player):
        if (self.round >= 8):
#            print ("Jack")
#            print(f"round: {self.round}")
            return -player
        if (self.round < 7 or len(self.cards) > 1) and np.count_nonzero(self.innocent) == 7:
#            print ("Detective")
#            print (f"round: {self.round}, cards: {len(self.cards)} innocent: {np.count_nonzero(self.innocent)}")
            return player
        return 0

