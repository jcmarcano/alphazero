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
    'batch_size': 320,
    'cuda': False,
    'num_channels': 128,
})


def normalize_board(game, board):

    GameInfo = np.ravel(board[2])
    n_extraInfo = np.zeros(7)

    # Main board

    # buttons
    ## _ = GameInfo[0:2] / 100

    pos = GameInfo[2:4]
    # Ignore Value
    ## self.value = GameInfo[4:6]
    buttonPos = GameInfo[6:8]
    
    # Distance to take buttons
    n_extraInfo[0:2] = buttonPos - pos


    # Distance to next 1x1 patch
    leatherPatchPos = GameInfo[8]
    n_extraInfo[2:4] = leatherPatchPos - pos

    # Ignore Player just moved
    ## _ = GameInfo[9]


    # get next 3 patches, sorted
    n_extraInfo[4:7] = np.sort(GameInfo[11:14])
    
    #NextPlayer
    if GameInfo[10] == 1:
        board3 = np.ones(board[0].shape) 
    else:
        board3 = np.zeros(board[0].shape) 
    n_boards = np.stack((board[0],board[1], board3), axis=2) # Third board has 1's if player 1 is next player, else 0's
    return [n_boards, n_extraInfo]


class NNetWrapper(NeuralNet):
    def __init__(self, game):
        self.nnet = onnet(game, args)
        self.action_size = game.getActionSize(net = True)
        self.game = game

    def initModel(self):
        self.nnet.compile()


    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))

        input_boards = np.array([normalize_board(self.game, board)[0] for board in input_boards])
        input_extra_infos = np.array([normalize_board(self.game, board)[1] for board in input_boards])
        target_pi0s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=1) for pi in target_pis])
        target_pi1s = np.array([np.sum(np.array(pi).reshape(self.action_size), axis=0) for pi in target_pis])
        target_vs = np.asarray(target_vs)
        
        self.nnet.model.fit(x=[input_boards, input_extra_infos], y=[target_pi0s, target_pi1s, target_vs], batch_size=args.batch_size, epochs=args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """

        norm_board = normalize_board(self.game, board)
        boards = np.array([norm_board[0]])
        extra_info = np.array([norm_board[1]])

        pi0, pi1, v = self.nnet.model.predict([boards, extra_info], verbose=False)


        pi = np.ravel(np.matmul(pi0[0][:,np.newaxis], pi1[0][np.newaxis,:]))  # policy prob is the product of the values of market an player actions

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
        if not os.path.isfile(filepath):
            return False
        
        self.nnet.model.load_weights(filepath)
        return True
