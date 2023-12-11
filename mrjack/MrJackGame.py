from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .MrJackLogic import Board
import numpy as np

class MrJackGame(Game):

    def __init__(self):
        pass

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board()
        cards = np.copy(b.cards)
        cards.resize(8)
        return np.concatenate((np.array([b.currentPlayer, b.round, b.witness, b.jack]), np.copy(b.visible), np.copy(b.innocent), cards))

    def getBoardSize(self):
        # (a,b) tuple
        return (28,)

    def getActionSize(self):
        # return number of actions
        return 8 * 2

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        b = Board(board)
        move = (int(action/2) + 1, action%2)
        # assert player == b.currentPlayer
        b.execute_move(move)
        cards = np.copy(b.cards)
        cards.resize(8)
        return (np.concatenate((np.array([b.currentPlayer, b.round, b.witness, b.jack]), np.copy(b.visible), np.copy(b.innocent), cards)), b.currentPlayer)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(board)
        legalMoves =  b.get_legal_moves()
        for x, y in legalMoves:
            valids[2*(x-1)+y]=1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(board)
        return b.game_ended(player)

    def getCanonicalForm(self, board, player):
        # There is no canonical form
        return np.copy(board)

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def stringRepresentation(self, board):
        return board.tostring()

    def stringRepresentationReadable(self, board):
        return board.tostring()

    @staticmethod
    def display(board):
        b = Board(board)
        s = "P: " + str(b.currentPlayer) + "        " + "R: " + str(b.round) + "\n" 
        s += "J: " + str(b.jack) + "        " + ("Visible" if b.witness else "Hidden") + "\n"
        initPos = 0 if len(b.cards) <= 4 else 4
        s += "C: " + np.array2string(b.cards[initPos: initPos + 4]) + "\n"
        s += "V: " + np.array2string(b.visible) + "\n"
        s += "I: " + np.array2string(b.innocent) + "\n"
        print(s)
