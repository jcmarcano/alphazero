import logging
import Agent
import numpy as np

log = logging.getLogger(__name__)

class AgentAlphZero(Agent):
       
    def getActionPolicy(self):
        return RandomPolicy()

class RandomPolicy():
    def __init__(self, game):
        self.game = game
    
    def getActionProb(self, canonicalBoard, temp=1):
        actionProbs = np.zeros(self.game.getActionSize())
        valids = self.game.getValidMoves(canonicalBoard, 1)
        action = np.random.choice(np.nonzero(valids)[0])

        actionProbs[action] = 1
        return actionProbs
