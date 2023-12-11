import unittest
import numpy as np
from patchwork.PatchworkGame import PatchworkGame


class JaipurTests(unittest.TestCase):
    def testGetIinitBoardSize(self):
        game = PatchworkGame(version = 1)
        board = game.getInitBoard()
#        print(board)


    def testGetBoardSize(self):
        self.assertEqual((3, 7, 7), PatchworkGame(version = 1).getBoardSize())
        self.assertEqual((3, 7, 7), PatchworkGame(version = 1).getInitBoard().shape)

    def testGetActiondSize(self):
        self.assertEqual(25 * 49 * 8, PatchworkGame(version = 1).getActionSize())



if __name__ == '__main__':

    game = PatchworkGame(version = 1)

    board = game.getInitBoard()
    print(board)
    moves = game.getValidMoves(board = board, player = 1)
    print (np.nonzero(moves)[0][5])
    board1, _ = game.getNextState(board, 1, np.nonzero(moves)[0][5])
    print(board1)
    moves1 = game.getValidMoves(board = board1, player = 1)
    movesCube = np.reshape(moves1, (25,8,7,7))

    for i in range(25):
        if i == 0 or i == 24:
            patchFigure = np.array([[1]])
        else:
            patchFigure = np.array(game.patches[i -1][0])

        for k in range(7):
            s = ""
            for j in range(8):
                for l in range(7):
                    opt = "OX" if board1[0,k,l] else ".X"
                    s += " " + opt[movesCube[i,j,k,l]] + " "
                s += "    "

            if k > 1 and k - 1 <= patchFigure.shape[0]:
                for m in range(patchFigure.shape[1]):
                    s += " " + " x"[patchFigure[k - 2,m]] + " "

            print(s)
        print ("")

    print("########################### BOARDS ########################################")
    print("")

    board2, _ = game.getNextState(board1, 2, 23*8*7*7 + 2*7 + 3)
    symetries = game.getSymmetries(board2, moves1)
    for i in range(3):
        for k in range(7):
            s=""
            for j in range(8):
                symBoard = symetries[j][0][i]
                for l in range(7):
                    if (symBoard[k,l]) < 10:
                        s+=" "
                    s += " " + str(int(symBoard[k,l])) + " "
                s += "    "
            print(s)
        print ("")

    print("########################## SYMETRIES #######################################")
    print("")


    patchNo = 14# int(np.nonzero(moves1)[0][0] / (8 * 7 * 7))
    print (patchNo)
    if patchNo == 0 or patchNo == 24:
        patchFigure1 = np.array([[1]])
    else:
        patchFigure1 = np.array(game.patches[patchNo - 1][0])

    for i in range(8):
        if i < 4:
            patchFigure2 = np.rot90(patchFigure1,i%4)
        else:
            patchFigure2 = np.rot90(np.flip(patchFigure1, axis = 0),i%4)
        for k in range(7):
            s=""
            for m in range(7):
                opt = "OX" if board1[0,k,m] else ".X"
                s += " " + opt[movesCube[patchNo,i,k,m]] + " "

            s += "  |  "
            for j in range(8):

                symBoard = symetries[j][0][0]
                symPositionsCube = np.reshape(symetries[j][1],(25,8,7,7))
                symPositions = symPositionsCube[patchNo,i]
                for l in range(7):
                    opt = "OX" if symBoard[k,l] else ".X"
                    s += " " + opt[int(symPositions[k,l])] + " "
                s += "    "

            if k > 1 and k - 1 <= patchFigure2.shape[0]:
                for n in range(patchFigure2.shape[1]):
                    s += " " + " x"[patchFigure2[k - 2,n]] + " "

            print(s)

        print ("")

    

    unittest.main()