import numpy as np
from jaipur.JaipurGame import JaipurGame


class RandomPlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a



class HumanPlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        options = np.where(valids == True)[0]
        while True:
            print("Valid moves:")
            for i, option in enumerate(options):
                move = JaipurGame().getMove((int(option/128), option%128))
                print (f"{i+1}: {move}")
            a = int(input())
            if a > 0 and a <= len(options):
                return options[a - 1]
            print('Invalid move')
