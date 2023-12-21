from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation, BatchNormalization, Dense, Dropout, Flatten, Input, Conv3D, Reshape
from tensorflow.keras.optimizers import Adam


class PatchworkNNet():

    def __init__(self, game, args):
        # game params
        self.board_z, self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize(net = True)
        self.args = args

        # Neural Net
        self.input_boards = Input(shape=(self.board_z * self.board_x * self.board_y, ))    # s: batch_size x board_x x board_y

        s_fc1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024)(self.input_boards))))  # batch_size x 512
        s_fc2 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024)(s_fc1))))  # batch_size x 512
        s_fc3 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512)(s_fc2))))  # batch_size x 512
        self.pi0 = Dense(self.action_size[0], activation='softmax', name='pi0')(s_fc3)   # batch_size x self.action_size (market action = 32)
        self.pi1 = Dense(self.action_size[1], activation='softmax', name='pi1')(s_fc3)   # batch_size x self.action_size (player action = 128)
        self.v = Dense(1, activation='tanh', name='v')(s_fc3)                    # batch_size x 1


        self.model = Model(inputs=self.input_boards, outputs=[self.pi0, self.pi1, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(args.lr))
