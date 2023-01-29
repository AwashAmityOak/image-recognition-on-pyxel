import os
os.chdir(os.path.dirname(__file__))
import pickle

import numpy as np

from mnist.mnist import load_mnist

def get_data():
	x_train: np.ndarray
	t_train: np.ndarray
	x_test: np.ndarray
	t_test: np.ndarray

	(x_train, t_train), (x_test, t_test) = \
		load_mnist(normalize=False, flatten=True, one_hot_label=False)
	
	return x_train, t_train, x_test, t_test

def sigmoid(x):
	return 1 / (1 + np.exp(-x))

def identity(x):
	return x

def softmax(a):
	c = np.max(a)
	exp_a = np.exp(a - c)
	sum_exp_a = np.sum(exp_a)
	y = exp_a / sum_exp_a
	return y

def init_network():
	with open("./mnist/sample_weight.pkl", "rb") as f:
		network = pickle.load(f)

	return network

def predict(network, x):
	W1: np.ndarray
	W2: np.ndarray
	W3: np.ndarray
	b1: np.ndarray
	b2: np.ndarray
	b3: np.ndarray

	W1, W2, W3 = [network["W"+str(i)] for i in range(1, 3+1)]
	b1, b2, b3 = [network["b"+str(i)] for i in range(1, 3+1)]

	W1 = W1.astype(np.float128)
	W2 = W2.astype(np.float128)
	W3 = W3.astype(np.float128)
	b1 = b1.astype(np.float128)
	b2 = b2.astype(np.float128)
	b3 = b3.astype(np.float128)

	a1 = np.dot(x, W1) + b1
	z1 = sigmoid(a1)
	a2 = np.dot(z1, W2) + b2
	z2 = sigmoid(a2)
	a3 = np.dot(z2, W3) + b3
	y = softmax(a3)

	return y

network = init_network()

def predict_one_number(x):
	y = predict(network, x)
	p = np.argmax(y)
	return p
