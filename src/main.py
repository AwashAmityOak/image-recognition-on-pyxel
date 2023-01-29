from typing import Optional

import pyxel

import pyxel_image_predict

def enlarge(image: pyxel.Image, rate_x: int, rate_y: Optional[int] = None):
	rate_y = rate_x if rate_y is None else rate_y
	enlarged = pyxel.Image(image.width*rate_x, image.height*rate_y)
	for y in range(image.height):
		for x in range(image.width):
			enlarged.rect(x*rate_x, y*rate_y, rate_x, rate_y, image.pget(x, y))
	return enlarged

def big_text(s: str, col: int, rate_x: int, rate_y: Optional[int] = None):
	original_image = pyxel.Image(
		pyxel.FONT_WIDTH*max(map(len, s.split("\n"))), 
		pyxel.FONT_HEIGHT*len(s.split("\n")), 
	)
	if col == 0: original_image.rect(0, 0, original_image.width, original_image.height, 1)
	original_image.text(0, 0, s, col)
	enlarged_image = enlarge(original_image, rate_x, rate_y)
	return (enlarged_image, 0, 0, enlarged_image.width, enlarged_image.height, (col == 0)+0)

class Button():
	def __init__(self, x, y, w, h, image: pyxel.Image, colkey=None):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.image = image
		self.colkey = colkey

	def on_mouse(self):
		x, y = pyxel.mouse_x, pyxel.mouse_y
		return self.x <= x and x < self.x+self.w and self.y <= y and y < self.y+self.h

	def btn(self):
		return pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.on_mouse()

	def btnp(self, *, hold=None, repeat=None):
		return pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, hold=hold, repeat=repeat) and self.on_mouse()

	def btnr(self):
		return pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.on_mouse()

	def draw(self):
		pyxel.blt(self.x, self.y, self.image, 0, 0, self.image.width, self.image.height, self.colkey)

class Cave_in_button(Button):
	def __init__(self, x, y, w, h, image: pyxel.Image, colkey=None, 
			*, frame_width, frame_light_color, frame_dark_color, 
		):
		super().__init__(x, y, w, h, image, colkey)
		self.frame_width = frame_width
		self.frame_light_color = frame_light_color
		self.frame_dark_color = frame_dark_color

		self.image_pushed = pyxel.Image(self.w, self.h)
		self.image_pushed.blt(
			self.frame_width, self.frame_width, 
			self.image, 0, 0, self.image.width, self.image.height
		)

		self.frame_colkey = \
			0 if not 0 in [frame_light_color, frame_dark_color] else \
			1 if not 1 in [frame_light_color, frame_dark_color] else 2
		self.frame_image_not_pushed = pyxel.Image(self.w, self.h)
		self.frame_image_pushed = pyxel.Image(self.w, self.h)
		self.frame_image_not_pushed.rect(
			0, 0, self.frame_image_not_pushed.width, self.frame_image_not_pushed.height, 
			self.frame_colkey
		)
		self.frame_image_pushed.rect(
			0, 0, self.frame_image_pushed.width, self.frame_image_pushed.height, 
			self.frame_colkey
		)

		self.frame_image_not_pushed.rect(
			0, 
			0, 
			self.frame_image_not_pushed.width, 
			self.frame_width, 
			self.frame_light_color, 
		)
		self.frame_image_not_pushed.rect(
			0, 
			0, 
			self.frame_width, 
			self.frame_image_not_pushed.height-self.frame_width, 
			self.frame_light_color, 
		)
		self.frame_image_not_pushed.rect(
			0, 
			self.frame_image_not_pushed.height-self.frame_width, 
			self.frame_image_not_pushed.width, self.frame_width, 
			self.frame_dark_color, 
		)
		self.frame_image_not_pushed.rect(
			self.frame_image_not_pushed.width-self.frame_width, 
			self.frame_width, 
			self.frame_width, 
			self.frame_image_not_pushed.height-self.frame_width, 
			self.frame_dark_color, 
		)

		self.frame_image_pushed.rect(
			0, 
			0, 
			self.frame_image_pushed.width, 
			self.frame_width, 
			self.frame_dark_color, 
		)
		self.frame_image_pushed.rect(
			0, 
			0, 
			self.frame_width, 
			self.frame_image_pushed.height-self.frame_width, 
			self.frame_dark_color, 
		)
		self.frame_image_pushed.rect(
			0, 
			self.frame_image_pushed.height-self.frame_width, 
			self.frame_image_pushed.width, self.frame_width, 
			self.frame_light_color, 
		)
		self.frame_image_pushed.rect(
			self.frame_image_pushed.width-self.frame_width, 
			self.frame_width, 
			self.frame_width, 
			self.frame_image_pushed.height-self.frame_width, 
			self.frame_light_color, 
		)

	def draw(self, is_push):
		pyxel.blt(
			self.x, self.y, 
			self.image_pushed if is_push else self.image, 
			0, 0, self.image.width, self.image.height, self.colkey, 
		)
		pyxel.blt(
			self.x, self.y, self.frame_image_pushed if is_push else self.frame_image_not_pushed, 
			0, 0, 
			self.frame_image_pushed.width, 
			self.frame_image_pushed.height, 
			self.frame_colkey
		)

class Canvas():
	def __init__(self, x, y, w, h, weight=1, color=pyxel.COLOR_BLACK):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.image = pyxel.Image(w, h)
		self.image.rect(
			0, 0, self.image.width, self.image.height, pyxel.COLOR_WHITE, 
		)

		self.weight = weight
		self.color = color

		self.is_drawing = False
		self.last_x, self.last_y = None, None

	def points_on_line(self, x1, y1, x2, y2):
		x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
		coordinates = []

		if abs(x1-x2) >= abs(y1-y2):
			try: 
				slope = (y1-y2) / (x1-x2)
			except ZeroDivisionError:
				slope = 0
			intercept = y1 - slope*x1
			for x in range(*((x2, x1+1) if x2 < x1 else (x1, x2+1))):
				coordinates.append((x, slope*x + intercept))
		else:
			try:
				slope = (x1-x2) / (y1-y2)
			except ZeroDivisionError:
				slope = 0
			intercept = x1 - slope * y1
			for y in range(*((y2, y1+1) if y2 < y1 else (y1, y2+1))):
				coordinates.append((slope*y + intercept, y))
		return coordinates

	def update(self):
		if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
			self.is_drawing = False
			self.last_x, self.last_y = None, None
			return

		mouse_x = pyxel.mouse_x-self.x
		mouse_y = pyxel.mouse_y-self.y

		if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and \
			0 <= mouse_x and mouse_x < self.w and 0 <= mouse_y and mouse_y < self.h:
				self.is_drawing = True
				self.last_x, self.last_y = mouse_x, mouse_y

		if not self.is_drawing:
			return

		coordinates = self.points_on_line(self.last_x, self.last_y, mouse_x, mouse_y)

		for point in coordinates:
			self.image.circ(*point, self.weight, self.color)

		self.last_x, self.last_y = mouse_x, mouse_y

	def draw(self):
		pyxel.blt(
			self.x, self.y, self.image, 
			0, 0, self.image.width, self.image.height, 
		)

class App():
	WIDTH = 256
	HEIGHT = 256 + 64
	TITLE = "Image Recognition"
	FPS = 60

	PENCIL = 0
	ERASER = 1

	def __init__(self):
		pyxel.init(self.WIDTH, self.HEIGHT, title=self.TITLE, fps=self.FPS)
		pyxel.mouse(True)

		self.canvas = Canvas(0, 0, self.WIDTH, self.WIDTH, weight=16)

		self.frame_coordinates = (0, self.WIDTH, self.WIDTH-1, self.HEIGHT-1)
		self.frame_pos_and_size = (0, self.WIDTH, self.WIDTH, self.HEIGHT-self.WIDTH)
		self.frame_color, self.frame_width = pyxel.COLOR_PINK, 4

		# Tool Buttons' Image
		pencil_image = pyxel.Image(16, 16)
		pencil_image.set(0, 0, [
			"0 0 0 0 0 0 0 0 0 0 E 0 0 0 0 0", 
			"0 0 0 0 0 0 0 0 0 E 0 E 0 0 0 0", 
			"0 0 0 0 0 0 0 0 E 0 0 0 E 0 0 0", 
			"0 0 0 0 0 0 0 E 0 0 0 0 0 E 0 0", 
			"0 0 0 0 0 0 E 0 0 0 0 0 0 0 E 0", 
			"0 0 0 0 0 E 0 0 0 0 0 0 0 0 0 E", 
			"0 0 0 0 E 0 0 0 0 0 0 0 0 0 E 0", 
			"0 0 0 E 0 0 0 0 0 0 0 0 0 E 0 0", 
			"0 0 E 0 0 0 0 0 0 0 0 0 E 0 0 0", 
			"0 E 0 0 0 0 0 0 0 0 0 E 0 0 0 0", 
			"E 0 0 0 0 0 0 0 0 0 E 0 0 0 0 0", 
			"E E 0 0 0 0 0 0 0 E 0 0 0 0 0 0", 
			"E E E 0 0 0 0 0 E 0 0 0 0 0 0 0", 
			"E E E E 0 0 0 E 0 0 0 0 0 0 0 0", 
			"E E E E E 0 E 0 0 0 0 0 0 0 0 0", 
			"E E E E E E 0 0 0 0 0 0 0 0 0 0", 
		])
		eraser_image = pyxel.Image(16, 16)
		eraser_image.set(0, 0, [
			"0 0 0 0 0 0 0 0 0 E 0 0 0 0 0 0", 
			"0 0 0 0 0 0 0 0 E 0 E 0 0 0 0 0", 
			"0 0 0 0 0 0 0 E 0 0 0 E 0 0 0 0", 
			"0 0 0 0 0 0 E 0 0 0 0 0 E 0 0 0", 
			"0 0 0 0 0 E 0 0 0 0 0 0 0 E 0 0", 
			"0 0 0 0 E 0 0 0 0 0 0 0 0 0 E 0", 
			"0 0 0 E 0 0 0 0 0 0 0 0 0 0 0 E", 
			"0 0 E 0 0 0 0 0 0 0 0 0 0 0 E 0", 
			"0 E 0 0 0 0 0 0 0 0 0 0 0 E 0 0", 
			"0 E E 0 0 0 0 0 0 0 0 0 E 0 0 0", 
			"E E E E 0 0 0 0 0 0 0 E 0 0 0 0", 
			"E E E E E 0 0 0 0 0 E 0 0 0 0 0", 
			"E E E E E E 0 0 0 E 0 0 0 0 0 0", 
			"0 E E E E E E 0 E 0 0 0 0 0 0 0", 
			"0 E E E E E E E 0 0 0 0 0 0 0 0", 
			"0 0 0 E E E 0 0 0 0 0 0 0 0 0 0", 
		])
		
		# Erase All Button's Image
		t, width, space, text_size = "Erase All", 2, 2, 2
		base_color, text_color, frame_light, frame_dark = \
			pyxel.COLOR_PINK, pyxel.COLOR_NAVY, \
			pyxel.COLOR_WHITE, pyxel.COLOR_PURPLE, 

		erase_all_image = pyxel.Image(
			pyxel.FONT_WIDTH*text_size*len(t)+(width+space)*2, 
			pyxel.FONT_HEIGHT*text_size+(width+space)*2, 
		)
		erase_all_image.rect(0, 0, erase_all_image.width, erase_all_image.height, base_color)
		erase_all_image.blt(width+space, width+space, *big_text(t, text_color, text_size))

		# Predict Button's Image
		t, width, space, text_size = "Predict", 2, 2, 2
		base_color, text_color, frame_light, frame_dark = \
			pyxel.COLOR_PINK, pyxel.COLOR_NAVY, \
			pyxel.COLOR_WHITE, pyxel.COLOR_PURPLE,

		predict_image = pyxel.Image(
			pyxel.FONT_WIDTH*text_size*len(t)+(width+space)*2, 
			pyxel.FONT_HEIGHT*text_size+(width+space)*2, 
		)
		predict_image.rect(0, 0, predict_image.width, predict_image.height, base_color)
		predict_image.blt(width+space, width+space, *big_text(t, text_color, text_size))

		# Tool Buttons
		pencil_relative_pos = [self.frame_width*3, self.frame_width*3]
		self.pencil_button = Button(
			*map(
				lambda x: x[1]+pencil_relative_pos[x[0]], 
				tuple(enumerate(self.frame_pos_and_size[:2])), 
			), 
			16, 16, pencil_image, 0, 
		)
		eraser_relative_pos = [self.frame_width*4+16, self.frame_width*3]
		self.eraser_button = Button(
			*map(
				lambda x: x[1]+eraser_relative_pos[x[0]], 
				tuple(enumerate(self.frame_pos_and_size[:2])), 
			), 
			16, 16, eraser_image, 0, 
		)

		# Erase All Button
		erase_all_relative_pos = [
			self.frame_width*3, self.frame_pos_and_size[3]-self.frame_width*3-erase_all_image.height
		]
		self.erase_all_button = Cave_in_button(
			*map(
				lambda x: x[1]+erase_all_relative_pos[x[0]], 
				tuple(enumerate(self.frame_pos_and_size[:2])), 
			), 
			erase_all_image.width, erase_all_image.height, erase_all_image, 
			frame_width=width, frame_light_color=frame_light, frame_dark_color=frame_dark
		)

		# Predict Button
		predict_relative_pos = [
			self.frame_pos_and_size[2]-self.frame_width*3-predict_image.width, 
			self.frame_pos_and_size[3]-self.frame_width*3-predict_image.height, 
		]
		self.predict_button = Cave_in_button(
			*map(
				lambda x: x[1]+predict_relative_pos[x[0]], 
				tuple(enumerate(self.frame_pos_and_size[:2])), 
			), 
			predict_image.width, predict_image.height, predict_image, 
			frame_width=width, frame_light_color=frame_light, frame_dark_color=frame_dark
		)

		w = self.frame_pos_and_size[3]-self.frame_width*3*2
		relative_pos = [
			(self.frame_pos_and_size[2]-w)/2, 
			self.frame_width*3, 
		]
		self.number_frame_sprite = (
			*map(
				lambda x: x[1]+relative_pos[x[0]], 
				tuple(enumerate(self.frame_pos_and_size[:2])), 
			), 
			w, w, pyxel.COLOR_PINK
		)

		self.tool = self.PENCIL

		self.erase_all_flag = False
		self.erase_all_original_count = self.FPS*1.5
		self.erase_all_count = self.erase_all_original_count
		self.draw_message_flag = False
		self.draw_message_original_count = self.FPS*3
		self.draw_message_count = self.draw_message_original_count
		self.predict_flag = False

		self.number = -1
		self.number_image = self.make_number_image(
			*self.number_frame_sprite[2:4], self.number, 6, 
			pyxel.COLOR_NAVY, pyxel.COLOR_PINK, 
		)

		pyxel.run(self.update, self.draw)

	def make_number_image(self, w, h, num, size, bg, col):
		image = pyxel.Image(w, h)
		image.rect(0, 0, image.width, image.height, bg)
		s = str(num) if 0 <= num else " "
		sprite = big_text(s, col, size)
		image.blt((w-sprite[3]+size)/2, (h-sprite[4]+size)/2, *sprite)
		return image

	def update(self):
		self.canvas.update()

		if self.pencil_button.btnp():
			self.tool = self.PENCIL
			self.canvas.color = pyxel.COLOR_BLACK
		if self.eraser_button.btnp():
			self.tool = self.ERASER
			self.canvas.color = pyxel.COLOR_WHITE
		if self.erase_all_button.btnp():
			self.erase_all_flag = True
		if self.erase_all_flag:
			if not pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
				self.erase_all_flag = False
				self.erase_all_count = self.erase_all_original_count
				self.draw_message_flag = True
				self.draw_message_count = self.draw_message_original_count
			self.erase_all_count -= 1
			if self.erase_all_count <= 0:
				self.canvas.image.rect(
					0, 0, self.canvas.image.width, self.canvas.image.height, 
					pyxel.COLOR_WHITE
				)
				self.erase_all_flag = False
				self.erase_all_count = self.erase_all_original_count
		if self.draw_message_flag:
			self.draw_message_count -= 1
			if self.draw_message_count <= 0:
				self.draw_message_flag = False
				self.draw_message_count = self.draw_message_original_count
		if self.predict_button.btnp():
			self.predict_flag = True
		if self.predict_flag:
			if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
				self.predict_flag = False
				self.number = pyxel_image_predict.predict(self.canvas.image, pyxel.COLOR_BLACK)
				self.number_image = self.make_number_image(
					*self.number_frame_sprite[2:4], self.number, 6, 
					pyxel.COLOR_NAVY, pyxel.COLOR_PINK, 
				)
			if not pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
				self.predict_flag = False

	def draw(self):
		pyxel.cls(0)
		self.canvas.draw()

		pyxel.rect(*self.frame_pos_and_size, pyxel.COLOR_NAVY)
		for i in range(self.frame_width):
			x, y, w, h = [value+i*[+1, -2][j//2] for j, value in enumerate(self.frame_pos_and_size)]
			pyxel.rectb(x, y, w, h, pyxel.COLOR_PINK)

		if self.tool == self.PENCIL: pyxel.pal(pyxel.COLOR_PINK, pyxel.COLOR_RED)
		self.pencil_button.draw()
		pyxel.pal()
		if self.tool == self.ERASER: pyxel.pal(pyxel.COLOR_PINK, pyxel.COLOR_RED)
		self.eraser_button.draw()
		pyxel.pal()
		self.erase_all_button.draw(self.erase_all_flag)
		pyxel.pal()
		if self.draw_message_flag:
			pyxel.text(
				self.frame_pos_and_size[0]+self.frame_width*5+16*2, 
				self.frame_pos_and_size[1]+self.frame_width*3, 
				"Long-press\nthe button\nto erase all.", pyxel.COLOR_PINK
			)
		pyxel.pal()
		self.predict_button.draw(self.predict_flag)
		pyxel.pal()

		pyxel.blt(
			*self.number_frame_sprite[:2], self.number_image, 
			0, 0, *self.number_frame_sprite[2:4]
		)
		for i in range(2):
			sprite = [value+i*[+1, -2, 0][j//2] for j, value in enumerate(self.number_frame_sprite)]
			pyxel.rectb(*sprite)
		pyxel.pal()

if __name__ == "__main__":
	App()
