import logging

import coloredlogs

from Coach import Coach
#from othello.OthelloGame import OthelloGame as Game
#from othello.pytorch.NNet import NNetWrapper as nn
#from jaipur.JaipurGame import JaipurGame as Game
#from jaipur.keras.NNet import NNetWrapper as nn
#from mrjack.MrJackGame import MrJackGame as Game
#from mrjack.keras.NNet import NNetWrapper as nn
from patchwork.PatchworkGame import PatchworkGame as Game
from patchwork.keras.NNet import NNetWrapper as nn

from utils import *

log = logging.getLogger(__name__)

coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

args = dotdict({
    'numIters': 1,
    'numEps': 4,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 30,        #
    'updateThreshold': 0.6,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 50,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 8,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,
    'verbose': True,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/jaipur','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})


def main():
##    fh = logging.FileHandler("output.log", 'w', 'utf-8')
##    log.addHandler(fh)
    log.info('Loading %s...', Game.__name__)
    g = Game(version=1)

    log.info('Loading %s...', nn.__name__)
#    nnet = nn(g)

    # if args.load_model:
    #     log.info('Loading checkpoint "%s/%s"...', args.load_folder_file[0], args.load_folder_file[1])
    #     nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    # else:
    #     log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
#    c = Coach(g, nnet, args)
    c = Coach(g, nn, args)
    if args.load_model:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')
    c.learn()


if __name__ == "__main__":
    main()
