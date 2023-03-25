import numpy as np

from layers.layer import Layer

def softmax(x: np.ndarray):
	keepdims = (not x.ndim == 1)
	exp_x = np.exp(x - np.max(x, axis=-1, keepdims=keepdims))
	return exp_x / np.sum(exp_x, axis=-1, keepdims=keepdims)

def cross_entropy_error(y: np.ndarray, t: np.ndarray):
	if y.ndim == 1:
		y = y.reshape(1, y.size)
		t = t.reshape(1, t.size)

	if t.size == y.size:
		t = t.argmax(axis=1)

	return -np.sum(np.log(y[np.arange(y.shape[0]), t] + 1e-7)) / y.shape[0]

class Softmax_with_loss(Layer):
	def __init__(self):
		super().__init__()

		self.y = None
		self.t = None

	def forward(self, x, t):
		self.t = t
		self.y = softmax(x)

		if self.t.size == self.y.size:
			self.t = self.t.argmax(axis=1)

		return cross_entropy_error(self.y, self.t)

	def backward(self, dout=1):
		if self.y is None or self.t is None:
			raise Exception("'forward()' is not executed")

		dx = self.y.copy()
		dx[np.arange(self.t.shape[0]), self.t] -= 1
		return dx * dout / self.t.shape[0]
