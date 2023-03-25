import numpy as np

from layers.layer import Layer

class Sigmoid(Layer):
	def __init__(self):
		super().__init__()

		self.out = None

	def forward(self, x):
		self.out = 1 / (1 + np.exp(-x))

		return self.out

	def backward(self, dout=1):
		if self.out is None:
			raise Exception("'forward()' is not executed")

		return dout * (1.0 - self.out) * self.out
