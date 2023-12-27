from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .PatchworkLogic import State
import numpy as np

# Orientations that are the result of apply a symetry, grouped by patch's orientation type

SYM_ORIENTATIONS = [
    [[0,0,0,0,0,0,0,0]],

    [[0,1,0,1,0,1,0,1],
     [1,0,1,0,1,0,1,0]],

    [[0,1,2,3,2,3,0,1],
     [1,2,3,0,1,2,3,0],
     [2,3,0,1,0,1,2,3],
     [3,0,1,2,3,0,1,2]],

    [[0,1,0,1,4,5,4,5],
     [1,0,1,0,5,4,5,4],
     [],
     [],
     [4,5,4,5,0,1,0,1],
     [5,4,5,4,1,0,1,0]],

    [[0,1,2,3,4,5,6,7],
     [1,2,3,0,7,4,5,6],
     [2,3,0,1,6,7,4,5],
     [3,0,1,2,5,6,7,4],
     [4,5,6,7,0,1,2,3],
     [5,6,7,4,3,0,1,2],
     [6,7,4,5,2,3,0,1],
     [7,4,5,6,1,2,3,0]]
]


class PatchworkGame(Game):

    def __init__(self, version = 1):
        st = State(version = version)
        self.version = version
        self.size = st.size
        self.patches = st.patches
        self.matchEnd = st.matchEnd
        self.orientations = 8
       

    def getInitBoard(self):
        # return initial board (numpy board)
        st = State(version = self.version)
        return st.getBoard()

    def getBoardSize(self):
        # (a,b) tuple
        return (3, self.size, self.size)

    def getActionSize(self, net = False):
        # return number of actions
        if net:
            return ((len(self.patches) + 2) * self.orientations, self.size * self.size)
        else:
            return (len(self.patches) + 2) * self.orientations * self.size * self.size   # Two additional actions plus place a patch: 1 - Place a 1x1 patch, 2. Advance and take buttons

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        st = State(version = self.version, board = board)
        
        patch = int(action / (self.orientations*self.size*self.size))
        orientation = int((action % (self.orientations*self.size*self.size)) / (self.size*self.size))
        position = action % (self.size*self.size)
        move = (patch, orientation, (int(position/self.size), position%self.size))
        st.DoMove(move, player)
        return st.getBoard(), st.getNextPlayer()

    def getNextPlayer(self, board, player):
        st = State(version = self.version, board = board)
        return st.getNextPlayer()

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        st = State(version = self.version, board = board)
        legalMoves =  st.GetMoves(player)
#        print(legalMoves)
        for patch, orientation, position in legalMoves:
            valids[patch * self.orientations * self.size * self.size  + orientation * self.size * self.size + position[0] * self.size + position[1]] = 1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        st = State(version = self.version, board = board)
        return st.GetResult(player)

    def getCanonicalForm(self, board, player):
        # Switch player boards
        if player == 1:
            return np.copy(board)

        newBoard = np.zeros(self.getBoardSize())

        # Boards
        newBoard[0] = np.copy(board[1])
        newBoard[1] = np.copy(board[0])

        GameInfo = np.copy(np.ravel(board[2]))
        newGameInfo = np.zeros(GameInfo.shape)

        # Player Info
        newGameInfo[0] = GameInfo[1]
        newGameInfo[1] = GameInfo[0]
        newGameInfo[2] = GameInfo[3]
        newGameInfo[3] = GameInfo[2]
        newGameInfo[4] = GameInfo[5]
        newGameInfo[5] = GameInfo[4]
        newGameInfo[6] = GameInfo[7]
        newGameInfo[7] = GameInfo[6]

        # Common values
        newGameInfo[8] = GameInfo[8]

        # Player Just Moved
        newGameInfo[9] = GameInfo[9] * player

        # Deck
        newGameInfo[10:] = np.copy(GameInfo[10:])

        newBoard[2] = np.reshape(newGameInfo, (self.size, self.size))

#        print ("Canonical Board")
#        print (newBoard)
        return newBoard

    def getSymmetries(self, board, pi):
        # There are symeties in the player boards. Options need to be asjusted to the board symetry
        st = State()

        totalPatches = len(self.patches) + 1 # Plus 1x1 Patch
        piCube = np.reshape(pi, (totalPatches + 1, 8, self.size, self.size)) # patches plus Advance Action

        symetries = []
        for symOrientation in range(self.orientations):
            # Calculate boards
            newBoard = np.array([st.getPatchOrientation(board[0], symOrientation), st.getPatchOrientation(board[1], symOrientation), np.copy(board[2])])

            # Calculate actions

            newPi = np.copy(piCube)
            # Update each patch action. less Advance Action
            for patchNo in range(len(self.patches) + 1): 
                if patchNo == 0:
                    orientationType = 0
                else:
                    patch=self.patches[patchNo-1]
                    orientationType = patch[4]

                # switch action orientations based on valid patch's orientations
                for patchOrientation in st.orientationTypes[orientationType]:
#                    print (f"patchOrientation: {patchOrientation}, orientationType: {orientationType}")
                    newOrientation = SYM_ORIENTATIONS[orientationType][patchOrientation][symOrientation]
#                    print (f"newOrientation: {newOrientation}")

                    positions = piCube[patchNo, patchOrientation] # Matrix of positions for patch and orientation actions

                    newPositions = self.getSymetryPositions(positions, patchNo, patchOrientation, symOrientation)

                    newPi[patchNo, newOrientation] = newPositions


            symetries.append((newBoard, np.copy(np.ravel(newPi))))
            action = np.argmax(newPi)
            p = int(action / (self.orientations*self.size*self.size))
            o = int((action % (self.orientations*self.size*self.size)) / (self.size*self.size))
            pos = action % (self.size*self.size)
            x = int(pos/7)
            y = pos%7

            if p > 0 and p < 24:
                po = st.getPatchOrientation(np.array(self.patches[p-1][0]), o)
                if x + po.shape[0] <=7 and y+po.shape[1] <= 7:
                    pass
                else:
#                    print(newBoard)
#                    print (f"sym: {symOrientation}, p: {p}, o: {o}, pos: ({x},{y})")
                    assert x + po.shape[0] <=7 and y+po.shape[1] <= 7

        return symetries

    def getSymetryPositions(self, positionPi, patchNo, patchOrientation, newOrientation):
        if patchNo == 0:
            h = 0
            v = 0
        else:
            patchFigure = np.array(self.patches[patchNo - 1][0])
            h = patchFigure.shape[1 - patchOrientation%2] - 1 
            v = patchFigure.shape[patchOrientation%2] - 1

        orientationOption = newOrientation if newOrientation < 4 else 7 - newOrientation

        if orientationOption == 0:
            shift = (0,0)
        elif orientationOption == 1:
            shift = (-h, 0)
        elif orientationOption == 2:
            shift = (-v, -h)
        else:
            shift = (0,-v)

        if newOrientation < 4:
            axis = (0,1)
        else: 
            axis = (1,0)

#        print (f"getSymetryPositions - positionPi: {positionPi}, newOrientation: {newOrientation}")

        return np.roll(State().getPatchOrientation(positionPi, newOrientation), shift, axis = axis)

    def stringRepresentation(self, board):
        return board.tostring()

    def stringRepresentationReadable(self, board):
        return board.tostring()

    @staticmethod
    def display(board):
        version = 1 if (board.shape == (3, 7, 7)) else 0
        st = State(version = version, board = board)
        print(st)
