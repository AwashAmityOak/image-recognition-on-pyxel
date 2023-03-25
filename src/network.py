import numpy as np

from layers import *

class FFNN():
	def __init__(self, *args, loss_layer=Softmax_with_loss, weight_init_std=0.01):
		self.layers = []

		for i in range(len(args)-1):
			if 0 < i: self.layers.append(Relu())
			self.layers.append(
				Affine(
					weight_init_std * np.random.randn(args[i], args[i+1]), 
					np.zeros(args[i+1]), 
				)
			)

		self.last_layer = loss_layer()

		self.params, self.grads = [], []

		for layer in self.layers:
			self.params += layer.params
			self.grads += layer.grads

	def predict(self, x):
		for layer in self.layers:
			x = layer.forward(x)
		return x

	def forward(self, x, t):
		return self.last_layer.forward(self.predict(x), t)

	def backward(self, dout=1):
		dout = self.last_layer.backward(dout)

		for layer in reversed(self.layers):
			dout = layer.backward(dout)

		return dout
