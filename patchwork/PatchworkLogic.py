import numpy as np
import random

# patches
# - figure
# - Time
# - Price
# - Value
# - Orientation Type (flip + rotation)
patchesExpress = [
# Colorful patches
[[[0,1],[1,1]],1,1,0,2],              # 1
[[[1,1,1],[0,0,1]],3,1,0,4],          # 2
[[[1,0,1],[1,1,1]],1,2,0,2],          # 3
[[[1,1,1],[0,1,1]],2,5,1,4],          # 4
[[[1,1,0],[0,1,1]],3,2,1,3],          # 5
[[[0,0,1],[1,1,1]],3,6,2,4],          # 6
[[[1,0,0],[1,1,0],[0,1,1]],3,0,0,2],  # 7
[[[1,0,0],[1,1,1],[0,0,1]],1,5,1,3],  # 8
[[[0,1,0],[1,1,1],[1,0,0]],4,2,1,4],  # 9
[[[0,0,1],[0,0,1],[1,1,1]],3,4,1,2],  #10
[[[1,0,0],[1,1,1],[1,0,0]],3,3,1,2],  #11
[[[0,1,0],[1,1,1],[0,1,0]],4,6,2,0],  #12
[[[0,0,1,0],[1,1,1,1]],1,3,0,4],      #13
[[[0,1,1,1],[1,1,0,0]],2,4,1,4],      #14
[[[1,1,1,1,1]],1,2,0,1],              #15

# Blue patches
[[[1,1]],2,0,1,1],                    #16
[[[1,1]],1,0,0,1],                    #17
[[[1,1]],2,4,2,1],                    #18
[[[1,1],[1,1]],1,3,0,0],              #19
[[[0,1],[1,1]],2,2,1,2],              #20
[[[1,1,1]],3,0,1,1],                  #21
[[[1,1,1]],1,2,0,1],                  #22
[[[1,1,1],[0,1,0]],2,3,1,2]           #23

]

leatherPatchPosExpress = 8
leatherPatchIncExpress = 4
buttonPosExpress = 6
buttonIncExpress = 4
matchEndExpress = 34


patchesFull = []


class State:
    def __init__(self, version = 1, board = None): # version: 0 = Full,1 = Express
        self.version = version
        if version == 0:
            self.size = 9
            self.patches = patchesFull
        else:
            self.size = 7
            self.leatherPatchInc = leatherPatchIncExpress
            self.buttonInitPos = buttonPosExpress
            self.buttonInc = buttonIncExpress
            self.matchEnd = matchEndExpress
            self.patches = patchesExpress

        if board is None:
            # Boards
            self.playerJustMoved = 1 
            self.board = np.zeros((2, self.size, self.size))
            self.pos = np.array([1,1])
            self.buttons = np.array([5,5])
            self.value = np.array([0,0])

            # Main board
            self.buttonPos = np.array([buttonPosExpress, buttonPosExpress])
            self.leatherPatchPos = leatherPatchPosExpress

            # Patches
            if version == 1:
                patchDeck = np.arange(2, 15 + 1)
            else:
                patchDeck = np.arange(2, len(self.patches) + 1)
            random.shuffle(patchDeck)
            self.patchDeck = np.append(patchDeck, [1])

        else:
            # Boards
            self.board = np.copy(board[0:2])

            GameInfo = np.copy(np.ravel(board[2]))

            # Main board
            self.buttons = GameInfo[0:2]
            self.pos = GameInfo[2:4]
            self.value = GameInfo[4:6]
            self.buttonPos = GameInfo[6:8]
            self.leatherPatchPos = GameInfo[8]
            self.playerJustMoved = GameInfo[9]
            # NExt Player not needed
            # _ = GameInfo[10]
            # Patches
            self.patchDeck = np.trim_zeros(GameInfo[11: 11 + len(self.patches) + 1])
#            print (f"Init patch deck: {self.patchDeck}")

        self.orientationTypes = [
            [0],
            [0,1],
            [0,1,2,3],
            [0,1,4,5],
            [0,1,2,3,4,5,6,7]
        ]

    def getBoard(self):
        patchDeck = np.copy(self.patchDeck)
        patchDeck.resize(len(self.patches))

        gameInfoTemp = np.concatenate((np.copy(self.buttons), np.copy(self.pos), np.copy(self.value), np.copy(self.buttonPos), np.array([self.leatherPatchPos, self.playerJustMoved, self.getNextPlayer()]), patchDeck))        
        gameInfoTemp.resize(self.size * self.size)
        gameInfo = np.reshape(gameInfoTemp, (1, self.size, self.size))
        return np.concatenate((np.copy(self.board), gameInfo))

    def DoMove(self, move, player):
        playerPos = 0 if player == 1 else 1
        patchNumber = move[0]
        orientation = move[1]
        position = move[2]

#        print(f"player: {player}, patchNumber: {patchNumber}, orientation: {orientation}, position: {position}")

        if patchNumber == 0: # place a 1x1 patch
            self.board[playerPos][position[0], position[1]]  = 1
            self.leatherPatchPos += self.leatherPatchInc
            self.playerJustMoved = player
#            print (self)
            return

        board = self.board[playerPos]
        if patchNumber == len(self.patches) + 1:  # Advance to take buttons
#            print(self)
            spaces =  self.pos[1 - playerPos] - self.pos[playerPos]
            if (self.pos[1 - playerPos] < self.matchEnd): spaces +=1

            # Take buttons
            self.buttons[playerPos] += spaces

            # Advance player pawn
            self.pos[playerPos] += spaces

#            print(self)
            assert(spaces > 0)

        else:  # Place Patch
            #Place a patch

            patch = self.patches[patchNumber - 1]
            patchFigure = self.getPatchOrientation(np.array(patch[0]), orientation)

            (patchHeight, patchWidth) = patchFigure.shape
#            print (board)
#            print (patchFigure)
#            print (patchHeight, patchWidth)
            board[position[0] : position[0] + patchHeight, position[1] : position[1] + patchWidth] += patchFigure
            if np.any(board [position[0] : position[0] + patchHeight, position[1] : position[1] + patchWidth] > 1):
                print(move)
                print(board)
                print(patchFigure)
            assert np.all(board [position[0] : position[0] + patchHeight, position[1] : position[1] + patchWidth] < 2)

            # Pay for patch
            self.buttons[playerPos] -= patch[2]
            
            # Update player value
            self.value[playerPos] += patch[3]

            # Advance player pawn
            self.pos[playerPos] += patch[1]

            # Remove patch from deck
            patchPos = np.argmax(self.patchDeck == patchNumber)
#            print (self.patchDeck)
#            print (f"Remove patch {patchNumber} in pos {patchPos}")

            self.patchDeck = np.append(self.patchDeck[patchPos + 1:],self.patchDeck[:patchPos])

            # For PatworkExpress, if there are 5 patches left, add blue tokens randomly
            if self.version == 1 and len(self.patchDeck) <= 5:
                bluePatches = np.arange(8) + 16
                random.shuffle(bluePatches)

                self.patchDeck = np.append(self.patchDeck,  bluePatches)


        # Update buttons when passing button mark
        if self.pos[playerPos] >= self.buttonPos[playerPos]:
            self.buttons[playerPos] += self.value[playerPos]
            self.buttonPos[playerPos] += self.buttonInc

        # if move is the last one, update button points
        if self.pos[playerPos] >= self.matchEnd:
            self.pos[playerPos] = self.matchEnd
            self.buttons[playerPos] -= (len(np.argwhere(board == 0)) * 2)

        self.playerJustMoved = player
#        print (self)



    def GetMoves(self, player):
        playerPos = 0 if player == 1 else 1

        if self.pos[playerPos] >= self.leatherPatchPos:
            # Next move = place leather patch
            positions = np.argwhere(self.board[playerPos]==0)
            if len(positions) > 0:
                moves = [(0,0,(p[0],p[1])) for p in positions ]
#                print(moves)
                return moves
        
        if self.pos[0] >= self.matchEnd and self.pos[1] >= self.matchEnd:
            return []
        
        # Get player board
        board = self.board[playerPos]

        moves = []

        # If first time, take options from one corner (avoid repeat symetric options)
        corner = 1 #2 if np.count_nonzero(board) == 0 else 1

        for deckPos in range(min(3, len(self.patchDeck))):

#            print (f"deckPos: {deckPos}, deck: {self.patchDeck}")
            patch = self.patches[int(self.patchDeck[deckPos] - 1)]

            # Use the patch if there is enough buttons
            if patch[2] <= self.buttons[playerPos]:
                patchFigure = np.array(patch[0])
                orientations = self.orientationTypes[patch[4]]

#                print (f"pos: {deckPos}, patch: {patchFigure}, orientations: {orientations}:")
                # Review all posible combinations
                for j in orientations:
                    patchOption = self.getPatchOrientation(patchFigure, j)

#                    print (f"figure: {patchOption}, shape: {patchOption.shape}")
                    # Find positions
                    for x in range(int((self.size - patchOption.shape[0])/corner)+1):
                        for y in range(int((self.size - patchOption.shape[1])/corner)+1):
#                            print(f"Move: ({self.patchDeck[deckPos]},{j},{x},{y}))")

                            # Validate patch orientation
                            fits = np.all(1 - np.multiply(board[x:x+patchOption.shape[0], y:y+patchOption.shape[1]],patchOption))
#                            print (f"fits: {fits}")
                            if fits: moves.append((int(self.patchDeck[deckPos]),j,(x,y)))

        # Advance Move
        if self.pos[playerPos] <= self.pos[1 - playerPos]:
            moves.append((len(self.patches) + 1,0,(0,0)))

#        print (moves)
#        print (len(moves))
        return moves


    def GetResult(self, player):
        ## TODO: Validate 7x7 bonus

        playerPos = 0 if player == 1 else 1

#        print (self.pos[0], self.pos[1])

        # Determine the number of buttons you have left , adding the value of the special tile (if available). From this score, subtract 2 points for each empty space of your quilt boar
        if self.pos[0] >= self.matchEnd and self.pos[1] >= self.matchEnd:
            value1 = self.buttons[playerPos] - len(np.argwhere(self.board[playerPos]==0)) * 2
            value2 = self.buttons[1 - playerPos] - len(np.argwhere(self.board[1 - playerPos]==0)) * 2
            if value1 > value2:
                return player
            if value2 > value1:
                return -player
            if self.playerJustMoved == player: # In case of a tie, the player who got to the final space of the time board first win
                return player
            else:
                return -player
        return 0


    def getPatchOrientation(self, patchFigure, orientation):
        newPatch = np.copy(patchFigure)
        if orientation >= 4:
            newPatch = np.flip(newPatch, axis = 0)
        return np.rot90(newPatch, orientation%4)
        
    def getNextPlayer(self):
        if self.pos[0] >= self.leatherPatchPos:
            return 1
        if self.pos[1] >= self.leatherPatchPos:
            return -1
        if (self.pos[0] < self.pos[1]):
            return 1
        if (self.pos[1] < self.pos[0]):
            return -1
        return self.playerJustMoved  # if both positions are equal, last player repeat

    def __repr__(self):
        s = ""
        for x in range(self.size):
            for board in range(2):
                for y in range(self.size):
                    s += ".x"[int(self.board[board][x,y])] + " "
                if board == 0 and x == 1:
                    if (self.buttons[0] < 10): s+= " "
                    s += "  " + str(int(self.buttons[0])) + "  "
                elif board == 0 and x == 2:
                    if (self.value[0] < 10): s+= " "
                    s += "  " + str(int(self.value[0])) + "  "
                elif board == 0 and x == 4:
                    if (self.buttons[1] < 10): s+= " "
                    s += "  " + str(int(self.buttons[1])) + "  "
                elif board == 0 and x == 5:
                    if (self.value[1] < 10): s+= " "
                    s += "  " + str(int(self.value[1])) + "  "
                else:
                    s+= "      "
            s+= "\n"
        for i in self.patchDeck:
            if (i < 10): s+= " "
            s += str(i) + " "
        s+= "\n"

        posLeatherPatch = self.leatherPatchPos
        posButton = self.buttonInitPos

        playerJMPos = 0 if self.playerJustMoved == 1 else 1
        for i in range (1, self.matchEnd + 1):
            
            if i == self.pos[playerJMPos]:
                s+= "12"[playerJMPos]
            elif i == self.pos[1 - playerJMPos]:
                s+= "12"[1 - playerJMPos]
            elif i == posLeatherPatch:
                s+= chr(9632)
            elif i == posButton:
                s+= "o"
            else:
                s+="."
            if i == posLeatherPatch:
                posLeatherPatch += self.leatherPatchInc
            if i == posButton:
                posButton += self.buttonInc

        s += "\n" + "BP: " + str(self.buttonPos[0]) + ", " + str(self.buttonPos[1]) + "\n" + "LPP: " + str(self.leatherPatchPos)
        s += "\n" + "POS: " + str(self.pos[0]) + ", " + str(self.pos[1])
        return s


