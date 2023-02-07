

import tensorflow as tf
from tensorflow.keras import layers
import pickle, os


inputs = layers.Input(shape=(50,), name = 'Input')
dense = layers.Dense(5, activation='relu', name='dense_layer')(inputs)
dense = layers.Dense(1,activation='linear', name='output_for_inference')(dense) 
output = layers.Activation('sigmoid', name='output_for_training')(dense)
model = tf.keras.Model(inputs, output, name = "model")


os.makedirs('jobs', exist_ok=True)


sorts = 10
inits = 5
seed  = 512
tag   = 'v1'


for sort in range(sorts):
    for init in range(inits):

        d = {
            'sort'      : sort,
            'init'      : init,
            'tag'       : tag,
            'seed'      : seed,
            'verbose'   : True,
            'batch_size': 1024,
            'loss'      : 'binary_crossentropy',
            'model'     : model.get_config(), 
            'weights'   : model.get_weights(),
        }

        o = 'jobs/job.%s.sort_%d.init_%d.pic'%(tag,sort,init)
        with open(o, 'wb') as f:
            pickle.dump(d, f)
