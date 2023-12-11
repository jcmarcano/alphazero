import numpy as np
import sys
import os
sys.path.append('..')
from utils import dotdict
from NeuralNet import NeuralNet

from .MrJackNNet import MrJackNNet as onnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': True,
    'num_channels': 512,
})


def normalize_board(board):


    newboard = np.zeros((24, ))
    #player 
    newboard[0] = 0 if board[0] < 0 else 1

    # Round
    newboard[1] = board[1] / 8 # Max round value

    # Witness
    newboard[2] = board[2]

    # Jack (0 if player is Detective)
    if board[0] != 1: 
        newboard[3] = board[3]

    # Visible & Innocent
    newboard[4:20] = board[4:20]

    # cards
    cards = np.trim_zeros(board[20:28])
    initPos = 20 if len(cards) <= 4 else 24
    newboard[20:24] = board[initPos:initPos + 4] / 8


    return newboard


class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = onnet(game, args)
        self.boardshape = (24, )
        self.action_size = 16

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))

        input_boards = np.array([normalize_board(board) for board in input_boards])
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        
        self.nnet.model.fit(x=input_boards, y=[target_pis,target_vs], batch_size=args.batch_size, epochs=args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """

        norm_board = normalize_board(board)
        norm_board = norm_board[np.newaxis, :]

        pi, v = self.nnet.model.predict(norm_board, verbose=False)

        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # change extension
        filename = filename.split(".")[0] + ".h5"
        
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # change extension
        filename = filename.split(".")[0] + ".h5"
        
        filepath = os.path.join(folder, filename)
        self.nnet.model.load_weights(filepath)
