import random
import math
import itertools

## Goods
CAMEL = 0
LEATHER = 1
SPICE = 2
CLOTH = 3
SILVER = 4
GOLD = 5
DIAMONDS = 6

## Actions
TAKE = 0
SELL = 1

## Bonus expected value
BONUS_3 = 2
BONUS_4 = 5
BONUS_5 = 9


## Good Tokens distribuition
# Sort the tokens by goods type.
# Make a pile for each goods type in order of value

GOOD_TOKENS = [[]]*7
GOOD_TOKENS[LEATHER]  = [1, 1, 1, 1, 1, 1, 2, 3, 4]
GOOD_TOKENS[SPICE]    = [1, 1, 2, 2, 3, 3, 5]
GOOD_TOKENS[CLOTH]    = [1, 1, 2, 2, 3, 3, 5]
GOOD_TOKENS[SILVER]   = [5, 5, 5, 5, 5]
GOOD_TOKENS[GOLD]     = [5, 5, 5, 6, 6]
GOOD_TOKENS[DIAMONDS] = [5, 5, 5, 7, 7]


MAX_ALLOWED_EXCHANGES = 10


class Board:
    def __init__(self, market = None, goods = None, playerInfo = None, cards = None, exchangeCount = None, player = None): 
        # Good Tokens
        if goods == None: 
            self.goods = [0]*7
            self.goods[LEATHER]  = 9
            self.goods[SPICE]    = 7
            self.goods[CLOTH]    = 7
            self.goods[SILVER]   = 5
            self.goods[GOLD]     = 5
            self.goods[DIAMONDS] = 5
        else:
            self.goods = goods

        # Cards
        if cards == None:
            self.cards = [0]*7
            self.cards[CAMEL]    = 8
            self.cards[LEATHER]  = 10
            self.cards[SPICE]    = 8
            self.cards[CLOTH]    = 8
            self.cards[SILVER]   = 6
            self.cards[GOLD]     = 6
            self.cards[DIAMONDS] = 6
        else:
            self.cards = cards

        if market == None:
            self.market = [CAMEL, CAMEL, CAMEL]   # Place 3 camel cards face up between the players
            self.SelectCard(self.market, numCards=2) # Take the first two cards from the deck and place them face up next to the camels. (Tere may well be 1 or 2 camels drawn.) Te market is now ready
        else:
            self.market = market

        self.playerHands = []
        self.playerHerds = []
        self.playerPoints = []
        if playerInfo == None:
            for i in range(2):
                self.playerHands.append([])
                self.SelectCard(self.playerHands[i], numCards=5)  # Deal 5 cards to each player.

                # The players then remove any camels from their hands and put them face up in a in a stack in front of them. This forms each player’s herd.
                self.playerHerds.append(0)
                if CAMEL in self.playerHands[i]: 
                    camelCount = self.playerHands[i].count(CAMEL)
                    self.playerHerds[i] += camelCount
                    self.playerHands[i] = self.playerHands[i][camelCount:]
                
                self.playerPoints.append(0) # Initial points = 0
        else:
            for i in range(2):
                self.playerHands.append(playerInfo[i][0])
                self.playerHerds.append(playerInfo[i][1])
                self.playerPoints.append(playerInfo[i][2])
        
        if player == None:
            self.playerJustMoved = 2 # At the root pretend the player just moved is p1 - p0 has the first move
        elif player == -1:
            self.playerJustMoved = 1
        else: 
            self.playerJustMoved = 2

        if exchangeCount == None:
            self.exchangeCount = 0
        else:
            self.exchangeCount = exchangeCount

    def SelectCard(self, target, numCards = 1):
        assert numCards <= sum(self.cards)

        for i in range(numCards):
            card = random.randrange(sum(self.cards))
            # print(f"random card {card}" )
            pos = 0
            selectedCard = -1
            for good in range(7):
                pos += self.cards[good]
                if (card < pos):
                    selectedCard = good
                    self.cards[good] -= 1
                    #self.availableCards -= 1
                    break
            assert selectedCard >= CAMEL

            target.append(selectedCard)
        target.sort()

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = Board()
        st.playerJustMoved = self.playerJustMoved
        st.market = [good for good in self.market]
        # print (self.goods)
        st.goods = [good for good in self.goods]
        st.cards = [good for good in self.cards]
        st.playerHands = [[good for good in self.playerHands[i]] for i in range(2)]
        st.playerHerds = [self.playerHerds[i] for i in range(2)]
        st.playerPoints = [self.playerPoints[i] for i in range(2)]
        #st.availableCards = self.availableCards
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        self.playerJustMoved = 3 - self.playerJustMoved

        playerHand = self.playerHands[self.playerJustMoved - 1]
        playerHerd = self.playerHerds[self.playerJustMoved - 1]
        playerPoints = self.playerPoints[self.playerJustMoved - 1]

#        print(f"move: {move}, market: {self.market}, hand: {playerHand}, herd: {playerHerd}")
        assert len(move) == 3
        action = move[0]
        marketCards = move[1]
        playerCards = move[2]
        assert action >= TAKE and action <= SELL


        if (action == TAKE):
            marketGoods = [self.market[card - 1] for card in marketCards]
            playerGoods = [playerHand[card - 1] for card in playerCards]
            camelCount = marketGoods.count(CAMEL)

#            print(f"market Goods: {marketGoods}, player Goods: {playerGoods}, camelCount: {camelCount}")
            assert (camelCount == 0 and ((len(marketCards) == 1 and len(playerCards) == 0) or (len(marketCards) > 1 and len(marketCards) >= len(playerCards)))) or camelCount == self.market.count(CAMEL)
            assert len(marketCards) <= len(self.market) and (len(playerHand) + (len(marketCards) - marketGoods.count(CAMEL)) - len(playerCards)) <= 7
            assert len(marketCards) < 2 or (len(marketCards) - camelCount - len(playerCards)) <= playerHerd

            for i, good in enumerate(marketGoods):
                self.market.remove(good)
                if (good == CAMEL):  # Take good action
                    playerHerd += 1
                else:
                    playerHand.append(good)
        
                if len(marketCards) >=2 and camelCount == 0: # If there are more than two cards from market and none of them are camels, this is an exchange action
                    if i < len(playerGoods):
                        playerGood = playerGoods[i]
#                        print(f"player Good: {playerGood}")
                        playerHand.remove(playerGood)
                        self.market.append(playerGood)
                    else: ## remaining exchange cards are camels
#                        print(f"good is a camel")
                        assert playerHerd > 0
                        playerHerd -= 1
                        self.market.append(CAMEL)

            if camelCount > 0: # Take camel action
                self.SelectCard(self.market, min(camelCount,sum(self.cards)))
                self.exchangeCount = 0
            elif len(marketCards) == 1: # Take good action
                self.SelectCard(self.market)
                self.exchangeCount = 0
            else: # Exchange action
                self.exchangeCount += 1

        elif (action == SELL):
            if len(playerCards) > len(playerHand):
                    print("ERROR len(playerCards) > len(playerHand) or len(goods) == 0")
                    print(self)
                    print (playerCards)
            goods = [playerHand[card - 1] for card in playerCards]
            assert len(playerCards) <= len(playerHand) and len(goods) > 0
            goodCount = len(goods)
            lastGood = goods[0]
            for good in goods:
                if (good != lastGood):
                    print("ERROR good != lastGood")
                    print(self)
                    print (playerCards)
                assert good == lastGood
                playerHand.remove(good)
                if (self.goods[good] > 0):
                    self.goods[good] -= 1
                    playerPoints += GOOD_TOKENS[good][self.goods[good]]
            if goodCount == 3 : playerPoints += BONUS_3
            elif goodCount == 4 : playerPoints += BONUS_4
            elif goodCount >= 5 : playerPoints += BONUS_5
            self.exchangeCount = 0


        self.market.sort()
        playerHand.sort()

        self.playerHands[self.playerJustMoved - 1] = playerHand
        self.playerHerds[self.playerJustMoved - 1] = playerHerd
        self.playerPoints[self.playerJustMoved - 1] = playerPoints

##        print(f"after move, market: {self.market}, hand: {playerHand}, herd: {playerHerd}, points: {playerPoints}")

    def isDeterministic(self):
        return False

    def gameEnded(self):
        ## END OF A ROUND
        # A round ends immediately if:
        # - 3 types of goods token are depleted.
        # - Tere are no cards left in the draw pile when trying to fill the market.

        return self.goods.count(0) >= 4 or sum(self.cards) == 0 ## End of game conditions


    def GetMoves(self, verbose=False):
        """ Get all possible moves from this state.
            Each move is a combination of the market cards and player cards used in the action
            Move = (Action Type, tuple with selecte market cards, tuple with selected player cards)
        """

        # Current player HAnd and Herd
        playerHand = self.playerHands[2 - self.playerJustMoved]
        playerHerd = self.playerHerds[2 - self.playerJustMoved]

        if verbose: print (f"Market: {self.market}, Hand: {playerHand}, Herd: {playerHerd}")

        ## END OF A ROUND
        # A round ends immediately if:
        # - 3 types of goods token are depleted.
        # - Tere are no cards left in the draw pile when trying to fill the market.

        if verbose: print(f"End conditions - Goods depleted: {self.goods.count(0)}, availableCards: {sum(self.cards)}")
        if self.gameEnded(): return []  ## End of game conditions

        # On your turn, you can either:
        # - Take Cards 
        # - Sale Cards
        # But never both!
        moves = []

        camelCount = self.market.count(CAMEL)


        ##### TAKE CARDS #####
        # If you take cards, you must choose one of the following options:
        # A take several goods (=EXCHANGE !),
        # B take 1 single good, 
        # C take all the camels.


        # A. Take several goods (Exchange)
        if (camelCount <= 3 and self.exchangeCount <= MAX_ALLOWED_EXCHANGES):
            cards = self.market[camelCount:]
            ## Take all the goods cards that you want into your hand (they can be of different types)
            for i in range(2, len(cards) + 1):
                moveOptions = set()
                for cardSet in itertools.combinations(cards, i): # Get all combination of at leat 2 cards in the market
                    # Create posible exchange options
                    moveOptions.add(cardSet)
                for moveOption in moveOptions:
                    validOptions = [CAMEL] * playerHerd + [card for card in playerHand if card not in moveOption] # Complete the set with camels
                    exchangeOptions = set()

                    # then ... exchange the same number of cards. Te returned cards can be camels, goods, or a combination of the two.
                    for exchangeSet in itertools.combinations(validOptions, i): ## Get all unique combinations of the same size of the market set (i)
                        exchangeOptions.add(exchangeSet)
                    for exchangeOption in exchangeOptions:
                        camelCountinSet = exchangeOption.count(CAMEL)
                        #print(f"playerHand: {playerHand}, moveOption: {moveOption}, exchangeOption{exchangeOption}, camelCountinSet: {camelCountinSet}")
                        if len(playerHand) + len(moveOption) - (len(exchangeOption) - camelCountinSet) <= 7: #Players may never have more than 7 cards in their hand at the end of their turn

                            # get the position of the selected cards in the market
                            pos = 0
                            marketCards = []
                            for good in moveOption:
                                pos = self.market.index(good, pos) + 1
                                marketCards.append(pos)
                            pos = 0

                            # get the position of the selected cards in the player hand
                            playerCards = []
                            for good in exchangeOption:
                                if good != CAMEL:
                                    pos = playerHand.index(good, pos) + 1
                                    playerCards.append(pos)
        
                            #print (f"marketCards: {marketCards}, playerCards: {playerCards}")

                            moves.append((TAKE, tuple(marketCards), tuple(playerCards)))

        # Take 1 single Good
        if (camelCount < 5 and len(playerHand) < 7): 
            # Take a single goods card from the market into your hand
            moves += [(TAKE, (i + 1,), ()) for i in range(5) if self.market[i] != CAMEL and (i == 1 or self.market[i-1] != self.market[i])] 

        # Take Camels
        if (camelCount > 0):
            # Take ALL the camels from the market and add them to your herd
            camelCards = tuple([i + 1 for i, card in enumerate(self.market) if card == CAMEL])
#            print(f"camelCards: {camelCards}")
            moves.append((TAKE,camelCards,()))

        ##### SELL CARDS #####
        if (len(playerHand) > 0):
            lastGood = 0
            cards = []
            for i, good in enumerate(playerHand):
                if good != lastGood:
                    if ((lastGood < SILVER and len(cards) >= 1) or (lastGood >= SILVER and len(cards) >= 2)): # When selling the 3 most expensive goods (diamonds, gold and silver), the sale must include a minimum of 2 cards
                        moves.append((SELL, (), tuple(cards)))
                    cards = []
                cards.append(i+1)
                lastGood = good

            if (lastGood < SILVER and len(cards) >= 1) or (lastGood >= SILVER and len(cards) >= 2): # When selling the 3 most expensive goods (diamonds, gold and silver), the sale must include a minimum of 2 cards
                moves.append((SELL, (), tuple(cards)))


        if verbose: print(f"moves: {moves}")  

        return moves
    
    def GetResult(self, playerjm):
        thisPlayerPos = playerjm - 1
        otherPlayerPos = 2- playerjm
        value = self.playerPoints[thisPlayerPos] - self.playerPoints[otherPlayerPos]
        if self.playerHerds[thisPlayerPos] > self.playerHerds[otherPlayerPos]:
            value += 5  ## Camel Bonus
        elif self.playerHerds[thisPlayerPos] < self.playerHerds[otherPlayerPos]:
            value -= 5
        return 1 / (1 + math.exp(-value))
##        return value
##        if value > 0: return 1.0
##        if value < 0: return 0.0
##        return 0.5
        
    def __repr__(self):
        text = ["CAME", "LEAT", "CLOT", "SPIC", "SILV", "GOLD", "DIAM"]
        s= ""
        for i in range(6):
            s += "MARKET"[i] + "  |  " + text[6-i] + ": "
            if (self.goods[6 - i]) > 0:
                s += str(GOOD_TOKENS[6 - i][self.goods[6 - i] - 1]) + " ("  + str(self.goods[6 - i]) + ")"
            else: 
                s += "-----"
            if i == 1:
                s+= "                      " + str(sum(self.cards))
            if i == 3:
                s += "     "
                for j in range(5):
                    s += text[self.market[j]] + "  "
            s += "\n"
        for i in range(2):
            s += "---+--------------------------------------------\n"
            s += "P  |  PTS: " + str(self.playerPoints[i]) + "\n"
            s += str(i+1) + "  |  CAM: " + str(self.playerHerds[i]) + "     "
            for j in range(len(self.playerHands[i])):
                s += text[self.playerHands[i][j]] + "  "
            s += "\n"
        return s
