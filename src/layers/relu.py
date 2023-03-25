from layers.layer import Layer

class Relu(Layer):
	def __init__(self):
		super().__init__()

		self.mask = None

	def forward(self, x):
		self.mask = (0 < x)

		return x * self.mask

	def backward(self, dout=1):
		if self.mask is None:
			raise Exception("'forward()' is not executed")

		return dout * self.mask
