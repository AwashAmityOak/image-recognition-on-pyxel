import numpy as np

from layers.layer import Layer

class Affine(Layer):
	def __init__(self, W: np.ndarray, b: np.ndarray):
		self.params = [W, b]
		self.grads = [np.zeros_like(W), np.zeros_like(b)]
		self.x = None

	def forward(self, x: np.ndarray):
		W, b = self.params

		self.x = x
		rx = self.x.reshape(-1, W.shape[0])

		out = np.dot(rx, W) + b

		return out.reshape(*self.x.shape[:-1], -1)

	def backward(self, dout: np.ndarray):
		if self.x is None:
			raise Exception("'forward()' is not executed")

		W, b = self.params

		rx = self.x.reshape(-1, W.shape[0])
		dout = dout.reshape(-1, W.shape[1])

		dx = np.dot(dout, W.T)
		dW = np.dot(rx.T, dout)
		db = np.sum(dout, axis=0)

		self.grads[0][...] = dW
		self.grads[1][...] = db

		return dx.reshape(self.x.shape)
