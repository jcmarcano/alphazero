import os

os.environ['CUDA_VISIBLE_DEVICES'] = ''

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue

queue = Queue()

def get_weights():
    from keras.models import Sequential
    import keras.backend as K
    import tensorflow as tf
    K.set_session(tf.Session())
    from keras.layers import Dense
    model = Sequential()
    model.add(Dense(512, input_shape=(500,)))
    model.compile('sgd', 'mse')
    return model.get_weights()

def pool_job(weights):
    from keras.models import Sequential
    import keras.backend as K
    import tensorflow as tf
    K.set_session(tf.Session())
    from keras.layers import Dense
    import numpy as np

    model = Sequential()
    model.add(Dense(512, input_shape=(500,)))
    model.compile('sgd', 'mse')
    model.set_weights(weights)
    while True:
        model.fit(np.ones([10, 500]), np.ones([10, 512]), 10, epochs=1)
        queue.put(os.getpid())


pool = ProcessPoolExecutor(3)
weights = pool.submit(get_weights).result()
[pool.submit(pool_job, weights)]

while True:
    print("Got:", queue.get(block=True))


###########################################################################
    
import os

os.environ['CUDA_VISIBLE_DEVICES'] = ''

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
import numpy as np

queue = Queue()


class Network():
    def __init__(self, path):
        from keras.models import load_model
        import keras.backend as K
        import tensorflow as tf
        K.set_session(tf.Session())
        self.model = load_model(path)

    def predict(self, img, **kwargs):
        return self.model.predict(img, verbose=0)


def pool_job(path):
    model = Network(path)
    while True:
        model.predict(np.ones([10, 500]))
        queue.put(os.getpid())


pool = ProcessPoolExecutor(3)
# weight.h5 is from model.save('weight.h5')
[pool.submit(pool_job, 'weight.h5') for _ in range(3)]

while True:
    print("Got:", queue.get(block=True))