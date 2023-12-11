import unittest
import numpy as np
from jaipur.JaipurGame import JaipurGame


class JaipurTests(unittest.TestCase):
    def testGetIinitBoardSize(self):
        game = JaipurGame()
        b = game.getInitBoard()
        self.assertTrue(np.array_equal(b[:3],np.array([0,0,0])))  # 3 camels in Market
        self.assertTrue(np.array_equal(b[5:11],np.array([9,7,7,5,5,5]))) # Initial good tokens
        self.assertTrue(np.array_equal(b[5:11],np.array([9,7,7,5,5,5]))) 


    def testGetBoardSize(self):
        self.assertEqual((37,), JaipurGame().getBoardSize())
        self.assertEqual((37,), JaipurGame().getInitBoard().shape)

    def testGetActiondSize(self):
        self.assertEqual(4096, JaipurGame().getActionSize())

    def testTakeGoodMoveAction(self):
        action = (4,0)
        move = JaipurGame().getMove(action)
        self.assertEqual((0, (4,), ()), move)

        action2 = JaipurGame().getAction(move)
        self.assertEqual((4,0), action2)

    def testTakeGoodMove(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          1, 3, 3, 6, 6, 0, 0, 
                          0, 0, 
                          1, 
                          7, 7, 8, 5, 5, 6, 2])
        bnext, player = JaipurGame().getNextState(board, 1, 4 * 128 + 0)   # (4, 0)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 3, 4, 6, 0, 0, 
                                                 1, 0, 
                                                 1, 3, 3, 6, 6, 0, 0, 
                                                 0, 0]),
                                       bnext[5:29])) # Market and cards will change

        bnext2, player = JaipurGame().getNextState(board, -1, 4 * 128 + 0)   # (4, 0)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0,
                                                 1, 0, 
                                                 1, 3, 3, 3, 6, 6, 0,
                                                 0, 0]),
                                       bnext2[5:29])) # MArket and card will change

    def testTakeCamelMoveAction(self):
        # Take camel in pos 1, 2, 3
        move = (0, (1, 2, 3), ())
        action = JaipurGame().getAction(move)
        self.assertEqual((16, 0), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((0, (1, 2, 3), ()), move2)

    def testTakeCamelMove(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          1, 3, 3, 6, 6, 0, 0, 
                          0, 0, 
                          1, 
                          7, 7, 8, 5, 5, 6, 2])
        bnext, player = JaipurGame().getNextState(board, 1, 16 * 128 + 0)   # (16, 0)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0, 
                                                 4, 0, 
                                                 1, 3, 3, 6, 6, 0, 0, 
                                                 0, 0]),
                                       bnext[5:29])) # Market and cards will change

        bnext2, player = JaipurGame().getNextState(board, -1, 16 * 128 + 0)   # (16, 0)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0,
                                                 1, 0, 
                                                 1, 3, 3, 6, 6, 0, 0,
                                                 3, 0]),
                                       bnext2[5:29])) # Market and cards will change

    def testExchangeMoveAction1(self):
        # Exchange market cards 4 and 5, with player card 1 and 2
        move = (0, (4, 5), (1, 2))
        action = JaipurGame().getAction(move)
        self.assertEqual((15, 8), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((0, (4, 5), (1, 2)), move2)

    def testExchangeMoveAction2(self):
        # Exchange market cards 4 and 5, with card 1 and a camel
        move = (0, (4, 5), (1, ))
        action = JaipurGame().getAction(move)
        self.assertEqual((15, 1), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((0, (4, 5), (1, )), move2)


    def testExchangeMoveAction3(self):
        # Exchange market cards 4 and 5, with 2 camels
        move = (0, (4, 5), ())
        action = JaipurGame().getAction(move)
        self.assertEqual((15, 0), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((0, (4, 5), ()), move2)

    def testExchangeMove(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          1, 3, 3, 6, 6, 0, 0, 
                          2, 0, 
                          1, 
                          7, 7, 8, 5, 5, 6, 2])
        bnext, player = JaipurGame().getNextState(board, 1, 15 * 128 + 8)   # (15, 8)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 3, 4, 6, 6, 0, 0, 0, 
                                                 1, 0, 
                                                 1, 3, 3, 6, 6, 0, 0, 
                                                 2, 0]),
                                       bnext[5:29]))
  
        bnext2, player = JaipurGame().getNextState(board, -1, 15 * 128 + 1)  # (15, 1)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0,
                                                 1, 0, 
                                                 3, 3, 3, 6, 6, 6, 0, 
                                                 1, 0]),
                                       bnext2[5:29]))

        bnext3, player = JaipurGame().getNextState(board, -1, 15 * 128 + 0)  # (15, 0)
        self.assertTrue(np.array_equal(np.array([9, 7, 7, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0,
                                                 1, 0, 
                                                 1, 3, 3, 3, 6, 6, 6,  
                                                 0, 0]),
                                       bnext3[5:29]))

    def testSellAction(self):
        # Exchange market cards 4 and 5, with player card 1 and 2
        move = (1, (), (1, 2))
        action = JaipurGame().getAction(move)
        self.assertEqual((0, 8), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((1, (), (1, 2)), move2)

    def testSellAction2(self):
        # Exchange market cards 4 and 5, with player card 1 and 2
        move = (1, (), (1, 2, 3))
        action = JaipurGame().getAction(move)
        self.assertEqual((0, 29), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((1, (), (1, 2, 3)), move2)


    def testSellAction3(self):
        # Exchange market cards 4 and 5, with player card 1 and 2
        move = (1, (), (4, 5))
        action = JaipurGame().getAction(move)
        self.assertEqual((0, 23), action)

        move2 = JaipurGame().getMove(action)
        self.assertEqual((1, (), (4, 5)), move2)

    def testSellMove(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          3, 3, 3, 6, 6, 0, 0, 
                          2, 0, 
                          1, 
                          7, 7, 8, 5, 5, 6, 2])
        bnext, player = JaipurGame().getNextState(board, 1, 0 * 128 + 8)   # (0, 8)

        self.assertTrue(np.array_equal(np.array([7, 7, 7, 5, 5, 5, 
                                                 4, 6, 0, 0, 0, 0, 0,
                                                 1, 7, 
                                                 3, 3, 3, 6, 6, 0, 0, 
                                                 2, 0]),
                                       bnext[5:29]))
        bnext2, player = JaipurGame().getNextState(board, -1, 0 * 128 + 29)  # (0, 29)

        self.assertTrue(np.array_equal(np.array([9, 7, 4, 5, 5, 5, 
                                                 1, 1, 4, 6, 0, 0, 0,
                                                 1, 0, 
                                                 6, 6, 0, 0, 0, 0, 0,
                                                 2, 13]),
                                       bnext2[5:29]))


    def testGetValidMoves(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          3, 3, 3, 6, 6, 0, 0, 
                          2, 0, 
                          7, 7, 8, 5, 5, 6, 2])
        # Valid Moves
        # (0, (4,), ())         =   (4, 0)  
        # (0, (5,), ())         =   (5, 0)
        # (0, (4, 5), (1,))     =   (15, 1)
        # (0, (4, 5), (3,))     =   (15, 3)
        # (0, (4, 5), (1, 2))   =   (15, 8)
        # (0, (4, 5), (1, 3))   =   (15, 9)
        # (0, (1, 2, 3), ())    =   (16, 0)
        # (1, (), (1, 2))       =   (0, 8)

        testValids = np.zeros(32*128)
        testValids[4 * 128 + 0] = 1
        testValids[5 * 128 + 0] = 1
        testValids[15 * 128 + 1] = 1
        testValids[15 * 128 + 3] = 1
        testValids[15 * 128 + 8] = 1
        testValids[15 * 128 + 9] = 1
        testValids[16 * 128 + 0] = 1
        testValids[0 * 128 + 8] = 1
        valids = JaipurGame().getValidMoves(board, 1)

        self.assertTrue(np.array_equal(testValids, valids))

        # Valid Moves
        # (0, (4,), ())         =   (4, 0)
        # (0, (5,), ())         =   (5, 0)
        # (0, (4, 5), ())       =   (15, 0)
        # (0, (1, 2, 3), ())    =   (16, 0)
        # (1, (), (4, 5))       =   (0, 23)
        # (1, (), (1, 2, 3))    =   (0, 29)

        testValids2 = np.zeros(32*128)
        testValids2[4 * 128 + 0] = 1
        testValids2[5 * 128 + 0] = 1
        testValids2[15 * 128 + 0] = 1
        testValids2[16 * 128 + 0] = 1
        testValids2[0 * 128 + 23] = 1
        testValids2[0 * 128 + 29] = 1
        valids2 = JaipurGame().getValidMoves(board, -1)

        self.assertTrue(np.array_equal(testValids2, valids2))

    def testGetValidMoves2(self):
        board = np.array([2, 4, 4, 4, 5,
                          5, 1, 2, 2, 0, 0,
                          3, 2, 2, 0, 0, 0, 0,
                          9, 41,
                          5, 6, 6, 6, 6, 6, 6,
                          2, 46,
                          1,
                          0, 0, 0, 0, 0, 0, 1])
        valids = JaipurGame().getValidMoves(board, -1)
        fv = valids.nonzero()[0]
        self.assertTrue(np.array_equal(np.array([126,  776,  782, 1166, 1288, 1294, 1550, 2077, 2092, 2348, 2845, 2860, 2988, 3392, 3412, 3540, 3924, 4082]), fv))

    def testGameEnded0(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          3, 3, 3, 6, 6, 0, 0, 
                          2, 0, 
                          7, 7, 8, 5, 5, 6, 2])
        self.assertEqual(0, JaipurGame().getGameEnded(board, 1))

    def testGameEnded1(self):
        board = np.array([0, 0, 0, 3, 6, 
                          1, 0, 0, 2, 0, 1, 
                          1, 1, 4, 6, 0, 0, 0, 
                          5, 78, 
                          3, 3, 3, 6, 6, 0, 0, 
                          5, 75, 
                          3, 2, 1, 1, 0, 0, 0])
        self.assertTrue(0 < JaipurGame().getGameEnded(board, 1))

    def testGameEnded2(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 1, 4, 6, 0, 0, 0, 
                          1, 0, 
                          3, 3, 3, 6, 6, 0, 0, 
                          2, 0, 
                          0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(0, JaipurGame().getGameEnded(board, 0))


    def testGetCanonicalForm(self):
        board = np.array([0, 0, 0, 3, 6, 
                          9, 7, 7, 5, 5, 5, 
                          1, 2, 3, 4, 5, 6, 7, 
                          8, 9, 
                          2, 3, 4, 5, 6, 7, 0, 
                          6, 7, 
                          1, 
                          7, 7, 8, 5, 5, 6, 2])
        
        self.assertTrue(np.array_equal(np.array([0, 0, 0, 3, 6, 
                                                 9, 7, 7, 5, 5, 5, 
                                                 1, 2, 3, 4, 5, 6, 7, 
                                                 8, 9, 
                                                 2, 3, 4, 5, 6, 7, 0, 
                                                 6, 7, 
                                                 1,
                                                 7, 7, 8, 5, 5, 6, 2]), 
                                       JaipurGame().getCanonicalForm(board,1)))
        self.assertTrue(np.array_equal(np.array([0, 0, 0, 3, 6, 
                                                 9, 7, 7, 5, 5, 5, 
                                                 2, 3, 4, 5, 6, 7, 0, 
                                                 6, 7, 
                                                 1, 2, 3, 4, 5, 6, 7, 
                                                 8, 9, 
                                                 1,
                                                 7, 7, 8, 5, 5, 6, 2]), 
                                       JaipurGame().getCanonicalForm(board,-1)))
        
    def testNormalizeBoard(self):
        canonical_board = np.array([0, 0, 0, 3, 6, 
                                    8, 7, 6, 5, 5, 3, 
                                    1, 1, 4, 6, 0, 0, 0, 
                                    1, 3, 
                                    3, 3, 3, 6, 6, 0, 0, 
                                    2, 5, 
                                    1, # Ignored
                                    7, 6, 8, 4, 5, 6, 2])
        normalized_board = np.array([0/6, 0/6, 0/6, 3/6, 6/6, 
                                    8/9, 7/7, 6/7, 5/5, 5/5, 3/5, 
                                    1/6, 1/6, 4/6, 6/6, 0/6, 0/6, 0/6, 
                                    1/11, ((-2.0 - 20.0) / (-20.0 - 20.0)) * (0.0 - 1.0) + 1.0,
                                    3/6, 3/6, 3/6, 6/6, 6/6, 0/6, 0/6, 
                                    2/11, 0., 
                                    (7 + 6 + 8 + 4 + 5 + 6 + 2) /40])
        self.assertTrue(np.array_equal(normalized_board, JaipurGame.normalizeBoard(canonical_board)))

        self.assertEqual(JaipurGame().getNormilizedBoardSize(), normalized_board.shape )

def testActionTupleVsNumber(self):
    a1 = np.array([0.001, 0.002, 0.997])
    a2 = np.array([0.001, 0.994, 0.002, 0.003])


    b1 = a1[:,np.newaxis]
    b2 = a2[np.newaxis,]

    x = np.matmul(b1, b2)

    y = np.ravel(x)

    out = np.ravel(np.matmul(a1[:,np.newaxis], a2[np.newaxis,:]))
    xr = y.reshape((3,4))

    assert (np.array_equal(x,xr))

    a1r = np.sum(out.reshape(3,4), axis=1)
    a2r = np.sum(out.reshape(3,4), axis=0)

    assert (np.array_equal(a1,a1r))
    assert (np.array_equal(a2,a2r))


if __name__ == '__main__':


    unittest.main()