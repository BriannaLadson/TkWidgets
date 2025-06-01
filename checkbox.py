from tkinter import Canvas, BooleanVar

class TkCheckbox(Canvas):
	def __init__(self, parent, variable=None, command=None, **kwargs):
		#Default Options
		self.options = {
			"bg": "white",
			"size": 25,
			"border_color": "black",
			"border_thickness": 6,
			"checkmark_width": 1,
			"checkmark_type": "checkmark", # "checkmark", "xmark"
			"checkmark_color": "black",
			"hover_bg": "lightgray",
			"disabled_color": "lightgray",
			"disabled_border_color": "lightgray",
		}
		
		self.options.update(kwargs)
		
		super().__init__(
			parent,
			bg=self.options["bg"],
			width=self.options["size"],
			height=self.options["size"],
		)
		
		self.disabled = False
		self.variable = variable if variable is not None else BooleanVar(value=False)
		self.command = command
		
		self.bind("<Configure>", self.draw_border)
		self.bind("<Button-1>", self.toggle)
		self.bind("<Enter>", self.on_enter)
		self.bind("<Leave>", self.on_leave)
		
	def config(self, **kwargs):
		self.options.update(kwargs)
		
		if "bg" in kwargs:
			self.config(bg=self.options["bg"])
			
		if "size" in kwargs:
			self.config(width=self.options["size"], height=self.options["size"])
			
		if "border_color" in kwargs or "border_thickness" in kwargs:
			self.draw_border()
			
		if "checkmark_type" in kwargs or "checkmark_width" in kwargs:
			self.draw_border()
			
		if "command" in kwargs:
			self.command = kwargs["command"]
		
	def draw_border(self, event=None):
		self.update_idletasks()
		
		self.delete("border", "checkmark")
		
		self.create_rectangle(
			0, 0,
			self.winfo_width(), self.winfo_height(),
			outline=self.options["border_color"],
			width=self.options["border_thickness"],
			tags="border",
		)
		
		if self.variable.get():
			getattr(self, "draw_" + self.options["checkmark_type"])()
			
			self.tag_raise("border")
		
	def draw_xmark(self):
		self.create_line(
			0, 0,
			self.winfo_width(),self.winfo_height(),
			tags="checkmark",
			width=self.options["checkmark_width"],
			fill=self.options["checkmark_color"],
		)
		
		self.create_line(
			0, self.winfo_height(),
			self.winfo_width(), 0,
			tags="checkmark",
			width=self.options["checkmark_width"],
			fill=self.options["checkmark_color"],
		)
		
	def draw_checkmark(self):
		size = min(self.winfo_width(), self.winfo_height())
		padding = size // 6
		
		x1, y1 = padding, size // 2
		x2, y2 = size // 2.5, size - padding
		x3, y3 = size - padding, padding
		
		self.create_line(
			x1, y1,
			x2, y2,
			width = self.options["checkmark_width"],
			fill=self.options["checkmark_color"],
			tags="checkmark",
		)
		
		self.create_line(
			x2, y2,
			x3, y3,
			width = self.options["checkmark_width"],
			fill=self.options["checkmark_color"],
			tags="checkmark",
		)
		
	def toggle(self, event=None):
		if self.disabled:
			return
			
		new_state = not self.variable.get()
		self.variable.set(new_state)
		self.draw_border()
		
		if self.command:
			self.command(new_state)
			
	def get(self):
		return self.variable.get()
		
	def set(self, value):
		self.variable.set(bool(value))
		self.draw_border()
		
	def on_enter(self, event=None):
		if not self.disabled:
			self.configure(bg=self.options["hover_bg"])
		
	def on_leave(self, event=None):
		if not self.disabled:
			self.configure(bg=self.options["bg"])
		
	def disable(self):
		self.disabled = True
		self.configure(bg=self.options["disabled_color"])
		self.options["original_border_color"] = self.options["border_color"]
		self.options["border_color"] = self.options["disabled_border_color"]
		self.draw_border()
		
	def enable(self):
		self.disabled = False
		self.configure(bg=self.options["bg"])
		self.options["border_color"] = self.options["original_border_color"]
		self.draw_border()