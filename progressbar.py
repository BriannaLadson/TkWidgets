from tkinter import Canvas

class TkProgressBar(Canvas):
	def __init__(self, parent, max_value=100, value=0, auto_increment=False, interval=1000, command=None, **kwargs):
		# Default Options
		self.options = {
			"width": 200,
			"height": 20,
			"bg": "white",
			"fill_color": "green",
			"border_color": "black",
			"border_thickness": 2,
			"show_text": True,
			"text_color": "black",
			"font": ("Arial", 10, "bold"),
		}
		self.options.update(kwargs)

		super().__init__(
			parent,
			width=self.options["width"],
			height=self.options["height"],
			bg=self.options["bg"],
			highlightthickness=0
		)

		self.max_value = max_value
		self.value = value
		self.auto_increment = auto_increment
		self.interval = interval
		self.command = command

		self.fill_rect = None
		self.text = None

		self.bind("<Configure>", self.redraw)

		if self.auto_increment:
			self.after(self.interval, self.step)

	def config(self, **kwargs):
		self.options.update(kwargs)

		if "bg" in kwargs:
			self.configure(bg=self.options["bg"])

		if "width" in kwargs or "height" in kwargs:
			# Resize the canvas
			self.config(
			width=self.options["width"],
			height=self.options["height"]
		)

		self.redraw()

	def set(self, value):
		self.value = max(0, min(value, self.max_value))
		self.redraw()

	def step(self, amount=1):
		self.set(self.value + amount)
		if self.auto_increment and self.value < self.max_value:
			self.after(self.interval, self.step)
		if self.command:
			self.command(self.value)

	def reset(self):
		self.set(0)

	def set_max(self, max_value):
		self.max_value = max_value
		self.redraw()

	def redraw(self, event=None):
		self.delete("all")

		width = self.winfo_width()
		height = self.winfo_height()

		progress = min(self.value / self.max_value, 1.0)
		fill_width = int(width * progress)

		# Draw filled portion first
		self.fill_rect = self.create_rectangle(
			0, 0, fill_width, height,
			fill=self.options["fill_color"],
			width=0
		)

		# Draw border on top
		self.create_rectangle(
			0, 0, width, height,
			width=self.options["border_thickness"],
			outline=self.options["border_color"]
		)

		# Draw text if enabled
		if self.options["show_text"]:
			percent = f"{int(progress * 100)}%"
			self.text = self.create_text(
			width // 2,
			height // 2,
			text=percent,
			fill=self.options["text_color"],
			font=self.options["font"]
		)

			
if __name__ == "__main__":
	from tkinter import Tk

	root = Tk()
	root.title("Progress Bar Test")

	bar = TkProgressBar(root, max_value=10, auto_increment=True, interval=1000)
	bar.pack(padx=20, pady=20)

	root.mainloop()
