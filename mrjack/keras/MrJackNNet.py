from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation, BatchNormalization, Dense, Dropout, Flatten, Input
from tensorflow.keras.optimizers import Adam


class MrJackNNet():

    def create_model(self, dropout):
        # Neural Net
        self.input_boards = Input(shape=self.input_shape)    # s: batch_size x board_x x board_y

        s_fc1 = Dropout(dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(16)(self.input_boards))))  # batch_size x 512
        s_fc2 = Dropout(dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(32)(s_fc1))))  # batch_size x 512
        s_fc3 = Dropout(dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(16)(s_fc2))))  # batch_size x 512
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc3)   # batch_size x self.action_size (market action = 32)
        self.v = Dense(1, activation='tanh', name='v')(s_fc3)                    # batch_size x 1

        return Model(inputs=self.input_boards, outputs=[self.pi, self.v])

    def __init__(self, game, args):
        # game params
        self.input_shape = (24, )
        self.action_size = 16
        self.args = args

        self.model = self.create_model(args.dropout)
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(args.lr))
