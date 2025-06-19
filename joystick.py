from tkinter import Canvas
import math

class TkJoystick(Canvas):
	def __init__(self, parent, command=None, **kwargs):
		self.options = {
			"bg": "white",
			"fg": "black",
			"size": 150,
			"stick_color": "black",
			"knob_color": "gray",
			"knob_ratio": .3,
			"output": "polar",
			"knob_outline_width": 5,
			"knob_outline_color": "darkgray",
			"stick_width": 2,
			"base_color": "black",
			"base_outline_width": 0,
			"base_outline_color": "black",
		}
		self.options.update(kwargs)
		
		bg = self.options["bg"]
		size = self.options["size"]
		
		super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
		
		self.command = command
		self.fg = self.options["fg"]
		self.stick_color = self.options["stick_color"]
		self.knob_color = self.options["knob_color"]
		self.size = size = self.options["size"]
		self.radius = size // 2
		self.knob_ratio = self.options["knob_ratio"]
		self.output = self.options["output"]
		self.deadzone = 0.05

		self.dx = 0
		self.dy = 0
		self.active = False

		self.bind("<Button-1>", self.activate)
		self.bind("<B1-Motion>", self.move)
		self.bind("<ButtonRelease-1>", self.release)

		self.draw_base()
		self.loop()

	def draw_base(self):
		self.delete("all")
		self.center = (self.radius, self.radius)
		self.knob_radius = int(self.radius * self.knob_ratio)

		self.create_oval(
			self.radius - self.radius, self.radius - self.radius,
			self.radius + self.radius, self.radius + self.radius,
			fill=self.options["base_color"],
			width=self.options["base_outline_width"],
			outline=self.options["base_outline_color"],
			tags="outer",
		)

		self.stick_line = self.create_line(
			self.center[0], self.center[1],
			self.center[0], self.center[1],
			fill=self.options["stick_color"], 
			width=self.options["stick_width"], 
			tags="stick",
		)

		self.knob = self.create_oval(
			self.center[0] - self.knob_radius, self.center[1] - self.knob_radius,
			self.center[0] + self.knob_radius, self.center[1] + self.knob_radius,
			fill=self.knob_color, 
			width=self.options["knob_outline_width"],
			outline=self.options["knob_outline_color"],
			tags="knob",
		)

	def activate(self, event):
		self.active = True
		self.move(event)

	def move(self, event):
		x = event.x - self.center[0]
		y = event.y - self.center[1]
		distance = math.sqrt(x ** 2 + y ** 2)
		max_distance = self.radius - self.knob_radius

		if distance > max_distance:
			scale = max_distance / distance
			x *= scale
			y *= scale

		self.dx = x / max_distance
		self.dy = y / max_distance
		self.update_knob_position()

	def release(self, event=None):
		self.active = False
		self.dx = 0
		self.dy = 0
		self.update_knob_position()

	def update_knob_position(self):
		x = self.dx * (self.radius - self.knob_radius)
		y = self.dy * (self.radius - self.knob_radius)

		self.coords("knob",
			self.center[0] + x - self.knob_radius,
			self.center[1] + y - self.knob_radius,
			self.center[0] + x + self.knob_radius,
			self.center[1] + y + self.knob_radius,
		)

		self.coords("stick",
			self.center[0], self.center[1],
			self.center[0] + x, self.center[1] + y
		)

	def get_vector(self):
		if abs(self.dx) < self.deadzone and abs(self.dy) < self.deadzone:
			return 0, 0
		return self.dx, self.dy

	def loop(self):
		if self.command:
			dx, dy = self.get_vector()
			if dx != 0 or dy != 0:
				if self.output == "polar":
					angle = math.degrees(math.atan2(-dy, dx)) % 360
					strength = math.sqrt(dx ** 2 + dy ** 2)
					self.command(angle, strength)
				else:
					self.command(dx, dy)
		self.after(16, self.loop)

if __name__ == "__main__":
	from tkinter import Tk, Canvas

	root = Tk()
	root.title("Joystick Demo")

	canvas = Canvas(root, width=300, height=300, bg="white")
	canvas.pack()

	player = canvas.create_oval(140, 140, 160, 160, fill="blue")

	def move_player(dx, dy):
		canvas.move(player, dx * 5, dy * 5)

	move_joystick = TkJoystick(root, output="cartesian", command=move_player)
	move_joystick.pack(pady=10)

	root.mainloop()
