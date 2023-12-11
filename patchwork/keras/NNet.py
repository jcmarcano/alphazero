import numpy as np
import sys
import os
sys.path.append('..')
from utils import dotdict
from NeuralNet import NeuralNet

from .PatchworkNNet import PatchworkNNet as onnet

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': True,
    'num_channels': 512,
})


def normalize_board(game, board):

    newBoard = np.zeros(board.shape)
    newBoard[0] = board[0]
    newBoard[1] = board[0]

    GameInfo = np.ravel(board[2])
    newGameInfo = np.zeros(GameInfo.shape)

    # Main board

    # buttons
    newGameInfo[0:2] = GameInfo[0:2] / 100

    # Player & Common Info
    newGameInfo[2:8] = GameInfo[2:8] / game.matchEnd

    #Player just moved
    newGameInfo[9] = GameInfo[9]

    # Patches
    newGameInfo[10:] = GameInfo[10:] / (len(game.patches) + 1)

    newBoard[2] = np.reshape(newGameInfo, (game.size, game.size))
    
    return newBoard


class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = onnet(game, args)
        self.action_size = game.getActionSize(net = True)
        self.game = game

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))

        input_boards = np.array([normalize_board(self.game, board) for board in input_boards])
        target_pi0s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=1) for pi in target_pis])
        target_pi1s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=0) for pi in target_pis])
        target_vs = np.asarray(target_vs)
        
        self.nnet.model.fit(x=input_boards, y=[target_pi0s, target_pi1s, target_vs], batch_size=args.batch_size, epochs=args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """

        norm_board = normalize_board(self.game, board)
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
