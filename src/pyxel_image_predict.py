import numpy as np
import pyxel

import recognition

def pyxel_image_to_ndarray(image: pyxel.Image, one_col: int) -> np.ndarray:
	array = np.zeros((image.height, image.width), dtype=np.float32)
	for y in range(image.height):
		for x in range(image.width):
			array[y][x] = 1 if image.pget(x, y) == one_col else 0
	return array

def resize(a: np.ndarray, size: tuple) -> np.ndarray:
	array = np.zeros(size, dtype=np.float32)
	for y in range(size[0]):
		for x in range(size[1]):
			before_y = y * a.shape[0] / size[0]
			before_x = x * a.shape[1] / size[1]
			data = []
			for v in range(int(before_y), int(before_y + a.shape[0] / size[0])):
				for u in range(int(before_x), int(before_x + a.shape[1] / size[1])):
					if not (0 <= v and v < a.shape[0]): continue
					if not (0 <= u and u < a.shape[1]): continue
					data.append(a[v][u])
			array[y][x] = sum(data) / len(data)
	return array

def predict(image: pyxel.Image, one_col):
	array = pyxel_image_to_ndarray(image, one_col)
	array = resize(array, (28, 28))
	y = recognition.predict_one_number(array.ravel())
	return y
