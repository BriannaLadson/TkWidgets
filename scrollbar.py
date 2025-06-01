from tkinter import Canvas

class TkScrollbar(Canvas):
	def __init__(self, parent, orient="vertical", command=None, **kwargs):
		#Default options
		self.options = {
			"bg": "#dddddd",
			"thumb_color": "#888888",
			"thumb_hover_color": "#666666",
			"thickness": 12,
		}
		self.options.update(kwargs)
		
		self.orient = orient
		self.command = command
		self.thumb_size = 30
		self.fraction = 0
		self.start_drag_pos = 0
		self.dragging = False
		self.hovering = False
		
		size_args = {"width": self.options["thickness"]} if orient == "vertical" else {"height": self.options["thickness"]}
		
		super().__init__(parent, bg=self.options["bg"], highlightthickness=0, **size_args)
		
		self.bind("<Button-1>", self.on_click)
		self.bind("<B1-Motion>", self.on_drag)
		self.bind("<Configure>", lambda e: self.redraw())
		self.bind("<ButtonRelease-1>", self.on_release)
		
	def config(self, **kwargs):
		self.options.update(kwargs)
		
		if "bg" in kwargs:
			self.configure(bg=self.options["bg"])
			
		if "thickness" in kwargs:
			if self.orient == "vertical":
				self.config(width=self.options["thickness"])
				
			else:
				self.config(height=self.options["thickness"])
				
		self.redraw()
		
	def set(self, first, last):
		size = self.winfo_height() if self.orient == "vertical" else self.winfo_width()
		self.fraction = float(first)
		self.thumb_size = max((float(last) - float(first)) * size, 20)
		self.redraw()
		
	def redraw(self):
		self.delete("thumb")
		size = self.winfo_height() if self.orient == "vertical" else self.winfo_width()
		max_pos = max(size - self.thumb_size, 1)
		pos = self.fraction * max_pos
		
		if self.orient == "vertical":
			self.create_rectangle(
				0, pos, 
				self.winfo_width(), 
				pos + self.thumb_size, 
				fill=self.options["thumb_hover_color"] if self.hovering or self.dragging else self.options["thumb_color"], 
				outline="", 
				tags="thumb"
			)
			
		else:
			self.create_rectangle(
				pos, 0,
				pos + self.thumb_size,
				self.winfo_height(),
				fill=self.options["thumb_hover_color"] if self.hovering or self.dragging else self.options["thumb_color"],
				outline="",
				tags="thumb"
			)
			
		self.tag_bind("thumb", "<Enter>", self.on_thumb_hover)
		self.tag_bind("thumb", "<Leave>", self.on_thumb_leave)
			
	def start_drag(self, event):
		self.start_drag_pos = event.y if self.orient == "vertical" else event.x
		
	def on_drag(self, event):
		self.dragging = True
		
		drag_pos = event.y if self.orient == "vertical" else event.x
		size = self.winfo_height() if self.orient == "vertical" else self.winfo_width()
		max_pos = max(size - self.thumb_size, 1)
		delta = drag_pos - self.start_drag_pos
		new_pos = max(0, min(self.fraction * max_pos + delta, max_pos))
		self.fraction = new_pos / max_pos
		
		if self.command:
			self.command("moveto", self.fraction)
			
		self.redraw()
		self.start_drag_pos = drag_pos
		
	def on_click(self, event):
		self.dragging = True
		
		click_pos = event.y if self.orient == "vertical" else event.x
		size = self.winfo_height() if self.orient == "vertical" else self.winfo_width()
		max_pos = max(size - self.thumb_size, 1)
		new_pos = max(0, min(click_pos - self.thumb_size / 2, max_pos))
		self.fraction = new_pos / max_pos
		
		if self.command:
			self.command("moveto", self.fraction)
			
		self.redraw()
		self.start_drag_pos = click_pos
		self.bind("<B1-Motion>", self.on_drag)
		
	def on_thumb_hover(self, event=None):
		self.hovering = True
		self.itemconfig("thumb", fill=self.options.get("thumb_hover_color", "#666666"))
		
	def on_thumb_leave(self, event=None):
		self.hovering = False
		if not self.dragging:
			self.itemconfig("thumb", fill=self.options.get("thumb_color", "#888888"))
		
	def on_release(self, event=None):	
		self.dragging = False
		self.itemconfig("thumb", fill=self.options.get("thumb_color", "#888888"))