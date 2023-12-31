import logging

import numpy as np
from tqdm import tqdm
from p_tqdm import p_map

log = logging.getLogger(__name__)


class Arena():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, display=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, gameNo=0, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        print(f"init game: {gameNo}")
        policies = [self.player2.getActionPolicy(), None, self.player1.getActionPolicy()]
        curPlayer = 1
        board = self.game.getInitBoard()
        it = 0
        while self.game.getGameEnded(board, curPlayer) == 0:
            it += 1
            if verbose:
                assert self.display
                self.display(board)
            action = np.argmax(policies[curPlayer + 1].getActionProb((self.game.getCanonicalForm(board, curPlayer))))

            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, curPlayer), 1)

            if valids[action] == 0:
                log.error(f'Action {action} is not valid!')
                log.debug(f'valids = {valids}')
                assert valids[action] > 0
            if verbose:
                print("Turn ", str(it), "Player ", str(curPlayer), "Action ", str(action) )
            board, curPlayer = self.game.getNextState(board, curPlayer, action)
        if verbose:
            assert self.display
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.display(board)
        return curPlayer * self.game.getGameEnded(board, curPlayer)

    def playGames(self, num, verbose=False, parallel=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0

        if parallel:
            for gameResult in p_map(self.playGame, range(num), [verbose]*num, desc="Arena.playGames (1)"):
                if gameResult == 1:
                    oneWon += 1
                elif gameResult == -1:
                    twoWon += 1
                else:
                    draws += 1

        else:
            for _ in tqdm(range(num), desc="Arena.playGames (1)"):
                gameResult = self.playGame(verbose=verbose)
                if gameResult == 1:
                    oneWon += 1
                elif gameResult == -1:
                    twoWon += 1
                else:
                    draws += 1

        self.player1, self.player2 = self.player2, self.player1

        if parallel:
            for gameResult in p_map(self.playGame, range(num), [verbose]*num, desc="Arena.playGames (2)"):
                if gameResult == -1:
                    oneWon += 1
                elif gameResult == 1:
                    twoWon += 1
                else:
                    draws += 1

        else:
            for _ in tqdm(range(num), desc="Arena.playGames (2)"):
                gameResult = self.playGame(verbose=verbose)
                if gameResult == -1:
                    oneWon += 1
                elif gameResult == 1:
                    twoWon += 1
                else:
                    draws += 1

        return oneWon, twoWon, draws
