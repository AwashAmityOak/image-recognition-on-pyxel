import os
os.chdir(os.path.dirname(__file__))
import pickle

import numpy as np

from network import FFNN

def init_network():
	with open("./assets/recognition_nn.pkl", "rb") as f:
		params = pickle.load(f)
	network = FFNN(
		*tuple([params[0].shape[0]] + [params[i].shape[1] for i in range(0, len(params), 2)])
	)
	for i in range(len(params)):
		network.params[i][:] = params[i]
	return network

network = init_network()

def predict_one_number(x):
	y = network.predict(x)
	p = np.argmax(y)
	return p
