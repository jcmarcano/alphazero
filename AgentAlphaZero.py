import logging
from Agent import Agent
from MCTS import MCTS

log = logging.getLogger(__name__)

class AgentAlphaZero(Agent):
    def __init__(self, game, nn, checkpointFileName, args):
        self.nn = nn
        self.checkpointFileName = checkpointFileName
        super().__init__(game, args)
       
    def getActionPolicy(self):
        nnet = self.nn(self.game)
        nnet.initModel()
        if not nnet.load_checkpoint(folder=self.args.checkpoint, filename=self.checkpointFileName):
            log.error(f"{self.checkpointFileName} not found")
            assert False
        return MCTS(self.game, nnet, self.args)
