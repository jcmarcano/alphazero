from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .JaipurLogic import Board
import numpy as np
import math
import itertools

class JaipurGame(Game):
    marketSize = 5
    handSize = 7
    goods = 6 # CAMEL + 6 GOODS
    herds = 1
    points = 1
    decks = 1
    playerInfoSize = handSize + herds + points
    exchangeCounter = 1   # Counter continuous exchanges


    market_actions = 32
    # Action Type           Actions     Values                  Combinations (Market cards, action Cards)
    # Sell                     1        ()                      1
    # Take Goods               5        (1,) .. (6,)            (5,1)
    # Exchange (Market)       26        (1,2) .. (1,2,3,4,5)    (5,2) + (5,3) + (5,4) + (5,5) [10 + 10 + 5 +1]
    # Take camels included in actions when all godds are camels

    player_actions = 128
    # Action Type           Actions     Values                  Combinations (Hand cards, action Cards)
    # Sell/Exchange (Hand)   128        () .. (1,2,3,4,5,6,7)   (7,0) + (7,1) + (7,2) + (7,3) + (7,4) + (7,5) + (7,6) + (7,7) [1 + 7 + 21 + 35 + 35 + 21 + 7 + 1]
    
    actionoptions = [(5, [1, 6, 16, 26, 31, 32], market_actions), 
                     (7, [1, 8, 29, 64, 99, 120, 127, 128], player_actions)]
    

    def getBoardFormat(self, b):
        market = np.array(b.market)
        if not np.array_equal(market, np.sort(market)):
            print(f"getBoardFormat -> Error in board market: {market}")
            print(b)
            assert False
        market.resize(5) # in the last round, the market could have less than 5 cards
        hand0 = np.array(b.playerHands[0])
        if not np.array_equal(hand0,np.sort(hand0)):
            print(f"getBoardFormat -> Error in board hand0: {hand0}")
            print(b)
            assert False
        hand0.resize(7)
        hand1 = np.array(b.playerHands[1])
        if not np.array_equal(hand1,np.sort(hand1)):
            print(f"getBoardFormat -> Error in board hand0: {hand1}")
            print(b)
            assert False
        hand1.resize(7)
        return np.concatenate((market, np.array(b.goods[1:JaipurGame.goods + 1]), 
                               hand0, np.array([b.playerHerds[0], b.playerPoints[0]]), 
                               hand1, np.array([b.playerHerds[1], b.playerPoints[1]]), 
                               np.array([b.exchangeCount]),
                               np.array(b.cards)))
    
    def getJaipurBoard(self, board, player=1):
        board = board.astype(int)
        market = list(board[0:JaipurGame.marketSize])
        market1 = market
        market1.sort()
        if (market != market1):
            print(f"getJaipurBoard -> Error in board market: {board}")
            assert False
        goods = [0] + list(board[JaipurGame.marketSize : JaipurGame.marketSize + JaipurGame.goods])
        playerInfo = []

        initPos = JaipurGame.marketSize + JaipurGame.goods
        for i in range(2):
            playerBoard = board[initPos + JaipurGame.playerInfoSize * i: initPos + JaipurGame.playerInfoSize * i + JaipurGame.playerInfoSize]
            hand = list(np.trim_zeros(playerBoard[:JaipurGame.handSize]))
            hand1 = hand
            hand1.sort()
            if (hand != hand1):
                print(f"getJaipurBoard -> Error in board hand: {board}")
                assert False
            herd, points = tuple(playerBoard[JaipurGame.handSize:])

            playerInfo.append((hand, herd, points))

        exchangeCount = board[initPos + JaipurGame.playerInfoSize * 2]
        cards = list(board[-JaipurGame.goods - 1:])
        return Board(market=market, goods=goods, playerInfo=playerInfo, cards=cards, exchangeCount=exchangeCount, player=player)

    def getInitBoard(self):
        # return initial board (numpy board)
        return self.getBoardFormat(Board())

    def getBoardSize(self):
        # (a,b) tuple This is the size of the canonical board
        return (JaipurGame.marketSize + JaipurGame.goods + (JaipurGame.handSize + JaipurGame.herds + JaipurGame.points) * 2 + JaipurGame.exchangeCounter + JaipurGame.goods + 1, )

    def getNormilizedBoardSize(self):
        # (a,b) tuple This is the size of the board used in the Neural Network (No exchange Counts, and total cards count instead of grouped by good type)
        return (JaipurGame.marketSize + JaipurGame.goods + (JaipurGame.handSize + JaipurGame.herds + JaipurGame.points) * 2 + JaipurGame.decks, )


    def getActionSize(self):
        # return number of actions
        # (market, excahnge) tuple
        return JaipurGame.market_actions * JaipurGame.player_actions

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move

        if action == 0:
            print ("invalid action")
            assert False

        if (board.shape != (37,)):
            print(f"getNextState -> board: {board} shape: {board.shape}")
            assert False

        b = self.getJaipurBoard(board, player)
        if (action != 0): 
            move = self.getMove((int(action/JaipurGame.player_actions), action % JaipurGame.player_actions))
            # print(f"getNextState -> move: {move}")
            b.DoMove(move)
        return self.getBoardFormat(b), -player

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*(self.getActionSize())
        b = self.getJaipurBoard(board, player)
        legalMoves =  b.GetMoves()

        # print(legalMoves)
        for move in legalMoves:
            marketAction, playerAction = self.getAction(move)
            valids[marketAction * JaipurGame.player_actions + playerAction]=1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1

        goods = list(board[JaipurGame.marketSize : JaipurGame.marketSize + JaipurGame.goods])
        herds = [0, 0]
        points = [0, 0]
        initPos = JaipurGame.marketSize + JaipurGame.goods
        for i in range(2):
            playerBoard = board[initPos + JaipurGame.playerInfoSize * i: initPos + JaipurGame.playerInfoSize * i + JaipurGame.playerInfoSize]
            herds[i], points[i] = tuple(playerBoard[JaipurGame.handSize:])

        cards = board[-JaipurGame.goods - 1 : ]
        # print(f"cards: {cards}")
        totalCards = np.sum(cards)

        # print(np.count_nonzero(goods))
        gameEnded = np.count_nonzero(goods) <= 3 or totalCards == 0
        # print(f"goods: {goods}, points: {points}, herds: {herds}, total cards: {totalCards}, gameEnded: {gameEnded}")
        if gameEnded:
            pointDiff = points[0] - points[1] + (5 if herds[0] > herds[1] else 0) - (5 if herds[1] > herds[0] else 0)
#            value = math.tanh(pointDiff / 2)  # Return a number between -1 and 1. The more large the difference, the more the value is near to 1 or -1
            value = np.sign(pointDiff)
            if value == 0:
                 # draw has a very little value 
                return 1e-4*player
            return value*player
        else:
            return 0

    def getCanonicalForm(self, board, player):
        # switch player info when player = -1

        if (board.shape != (37,)):
            print(f"getCanonicalForm -> board: {board} shape: {board.shape}")
            assert(False)

        newBoard = np.zeros(self.getBoardSize(), dtype=int)
        initPos = JaipurGame.marketSize + JaipurGame.goods
        player0Pos = initPos
        player1Pos = player0Pos + JaipurGame.playerInfoSize
        endPlayerPos = player1Pos + JaipurGame.playerInfoSize

        newBoard[:endPlayerPos] = board[:endPlayerPos]
        if (player == -1):
            newBoard[player0Pos : player1Pos] = board[player1Pos : endPlayerPos]
            newBoard[player1Pos : endPlayerPos] = board[player0Pos : player1Pos]

        newBoard[endPlayerPos: endPlayerPos + 1] = board[endPlayerPos: endPlayerPos + 1]
        newBoard[-JaipurGame.goods - 1 : ] = board[-JaipurGame.goods - 1 : ]

        return newBoard

    def getSymmetries(self, board, pi):
        # There is no symetries. To avoid symetries calculations:
        # - Market and Player cards are always sorted
        # - The deck is sumarized as a total number of cards in the board used in the netowrk
        # - Exchange counter is ignored

        # There is a node in the tree for each combination, but the value is calculated once in the network
        return [(board, pi)]

    def stringRepresentation(self, board):
        return board.tostring()

    def stringRepresentationReadable(self, board):
        return board.tostring()
    
    @staticmethod
    def normalizeBoard(board):

        newboard = np.zeros(30)
        #market 
        newboard[0:5] = board[0:5] / 6 # Max good value

        #goods
        newboard[5:11] = board[5:11] / np.array([9,7,7,5,5,5])  # Chips on each stack

        #player0 cards
        newboard[11:18] = board[11:18] / 6  # Max good value

        #player0 herd
        newboard[18] = board[18] / 11   # Total herds

        # Pos 19 and 28 are calculated later

        #player1 cards
        newboard[20:27] = board[20:27] / 6  # Max good value

        #player1 herd
        newboard[27] = board[27] / 11   # Total herds

        # Exchange count is ignored!
        # Pos 19 and 28 are calculated later

        #deck
        newboard[29] = np.sum(board[-JaipurGame.goods - 1 : ]) / 40   # Sum of Cards ( there are 40 cards available after init board)

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


    @staticmethod
    def display(board):
        b = JaipurGame().getJaipurBoard(board)
        print(b)


    def getMove(self, action):
        marketAction = action[0]
        playerAction = action[1]

        marketMove = self.getMoveCombination(marketAction, JaipurGame.actionoptions[0])
        playerMove = self.getMoveCombination(playerAction, JaipurGame.actionoptions[1])

        if (marketMove == ()):
            moveType = 1 ## Sell Goods
        else:
            moveType = 0 ## Take Goods

        return (moveType, marketMove, playerMove)


    def getAction(self, move):
        marketmove = move[1]
        playermove = move[2]

        marketAction = self.getActionValue(marketmove, JaipurGame.actionoptions[0])
        playerAction = self.getActionValue(playermove, JaipurGame.actionoptions[1])


        return (marketAction, playerAction)


    def getMoveCombination(self, actionValue, option):
        initPos = 0
        for pos, value in enumerate(option[1]):
            if actionValue < value:
                options = pos
                break
            else:
                initPos = actionValue - value
        move = ()
        if (options > 0):
            for pos, combination in enumerate(itertools.combinations(range(1, option[0] + 1), options)):
                if pos == initPos:
                    move = combination
                    break
        
        return move

    def getActionValue(self, move, option):
        if move == (): return 0
        options = len(move)
        initPos = option[1][options - 1]

        action = 0
        for pos, combination in enumerate(itertools.combinations(range(1, option[0] + 1), options)):
            if move == combination:
                action = initPos + pos
                break

        return action

