import numpy as np
import sys
import os
sys.path.append('..')
from utils import dotdict
from NeuralNet import NeuralNet

from .JaipurNNet import JaipurNNet as onnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': True,
    'num_channels': 512,
})


def normalize_board(board):

    newboard = np.zeros((30, ))
    #market 
    newboard[0:5] = board[0:5] / 6 # Max good value

    #goods
    newboard[5:11] = board[5:11] / np.array([9,7,7,5,5,5])  # Chips on each stack

    #player0 cards
    newboard[11:18] = board[11:18] / 6  # Max good value

    #player0 herd
    newboard[18] = board[18] / 11   # Total herds

    #player1 cards
    newboard[20:27] = board[20:27] / 6  # Max good value

    #player1 herd
    newboard[27] = board[27] / 11   # Total herds

    #deck
    newboard[29] = np.sum(board[-7:]) / 40   # Cards after init board

    # points
    p0_score = board[19]
    p1_score = board[28]
    score = p0_score - p1_score
    max_score = 20.0
    min_score = -max_score
    if score > max_score: score = max_score
    if score < min_score: score = min_score

    min_normalized, max_normalized = 0, 1
    normalized_score = ((score - max_score) / (min_score - max_score)) * (min_normalized - max_normalized) + max_normalized

    newboard[19] = normalized_score
    newboard[28] = 0

    return newboard


class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = onnet(game, args)
        self.boardshape = (30, )
        self.action_size = (32, 128)

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))

        input_boards = np.array([normalize_board(board) for board in input_boards])
        target_pi0s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=1) for pi in target_pis])
        target_pi1s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=0) for pi in target_pis])
        target_vs = np.asarray(target_vs)
        
        self.nnet.model.fit(x=input_boards, y=[target_pi0s, target_pi1s, target_vs], batch_size=args.batch_size, epochs=args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """

        norm_board = normalize_board(board)
        norm_board = norm_board[np.newaxis, :]

        pi0, pi1, v = self.nnet.model.predict(norm_board, verbose=False)

        pi = np.ravel(np.matmul(pi0[0][:,np.newaxis], pi1[0][np.newaxis,:]))  # politic prob is the product of the values of market an player actions

        return pi, v[0]

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
