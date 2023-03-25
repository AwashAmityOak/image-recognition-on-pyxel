class Layer():
	def __init__(self):
		self.params, self.grads = [], []

	def forward(self):
		raise NotImplementedError()

	def backward(self, dout):
		raise NotImplementedError()
