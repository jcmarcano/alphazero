from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation, BatchNormalization, Dense, Dropout, Flatten, Input, Conv2D, Reshape, Concatenate
from tensorflow.keras.optimizers import Adam


class PatchworkNNet():

    def __init__(self, game, args):
        # game params
        self.board_z, self.board_x, self.board_y = game.getBoardSize()
        self.extraInfoSize = 2 + 2 + 3
        self.action_size = game.getActionSize(net = True)
        self.args = args

        # Neural Net
        #self.input_boards = Input(shape=(self.board_z, self.board_x, self.board_y))    # s: batch_size x board_x x board_y
        self.input_boards = Input(shape=(self.board_x, self.board_y, self.board_z))
        self.input_extra_info = Input(shape=(self.extraInfoSize, ))    # s: batch_size x board_x x board_y

        #xboards_image = Reshape((self.board_z, self.board_x, self.board_y, 1))(self.input_boards)                # batch_size  x board_x x board_y x 1
        xboards_image = self.input_boards
        h_conv1 = Activation('relu')(BatchNormalization()(Conv2D(args.num_channels, 3, padding='same')(xboards_image)))         # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization()(Conv2D(args.num_channels, 3, padding='same')(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization()(Conv2D(args.num_channels, 3, padding='same')(h_conv2)))        # batch_size  x (board_x) x (board_y) x num_channels
        h_conv4 = Activation('relu')(BatchNormalization()(Conv2D(args.num_channels, 3, padding='valid')(h_conv3)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4_flat = Flatten()(h_conv4)       
        h_ef1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(16)(self.input_extra_info))))  # batch_size x 16
        h_ef2 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(16)(h_ef1))))  # batch_size x 16
        h_concat = Concatenate()([h_conv4_flat, h_ef2])       
        s_fc1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(256)(h_concat))))  # batch_size x 256
        s_fc2 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(256)(s_fc1))))          # batch_size x 256
        self.pi0 = Dense(self.action_size[0], activation='softmax', name='pi0')(s_fc2)   # batch_size x self.action_size
        self.pi1 = Dense(self.action_size[1], activation='softmax', name='pi1')(s_fc2)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)                    # batch_size x 1


    def compile(self, weigths = None):
        self.model = Model(inputs=[self.input_boards, self.input_extra_info], outputs=[self.pi0, self.pi1, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(self.args.lr))
        if weigths:
            self.model.set_weigths(weigths)

