from tkinter import Canvas

class TkScrollbar(Canvas):
	def __init__(self, parent, orient="vertical", command=None, **kwargs):
		#Default options
		self.options = {
			"bg": "#dddddd",
			"thumb_color": "#888888",
			"thumb_hover_color": "#666666",
			"thickness": 12,
			"gradient_thumb": ((0,0,0), (255,255,255)),
			"animation": None,
		}
		self.options.update(kwargs)
		
		self.orient = orient
		self.command = command
		self.thumb_size = 30
		self.fraction = 0
		self.start_drag_pos = 0
		self.dragging = False
		self.hovering = False
		self.anim_offset = 0
		self.pulse_strength = 0.0
		self.pulse_direction = 1
		
		size_args = {"width": self.options["thickness"]} if orient == "vertical" else {"height": self.options["thickness"]}
		
		super().__init__(parent, bg=self.options["bg"], highlightthickness=0, **size_args)
		
		if isinstance(self.options["gradient_thumb"], tuple):
			self.options["gradient_thumb"] = list(self.options["gradient_thumb"])
		
		self.bind("<Button-1>", self.on_click)
		self.bind("<B1-Motion>", self.on_drag)
		self.bind("<Configure>", lambda e: self.redraw())
		self.bind("<ButtonRelease-1>", self.on_release)
		
		if self.options["animation"]:
			self.after(50, self.animate)
			self.options["thumb_color"] = None
		
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
		
		anim = self.options.get("animation")
		if anim == "scroll":
			self.draw_gradient_scroll(pos)
			
		elif anim == "pulse":
			self.draw_gradient_pulse(pos)
			
		elif anim == "shimmer":
			self.draw_shimmer(pos)
			
		else:
			self.draw_thumb(pos, self.options["thumb_hover_color"] if self.hovering or self.dragging else self.options["thumb_color"])
			
		self.tag_bind("thumb", "<Enter>", self.on_thumb_hover)
		self.tag_bind("thumb", "<Leave>", self.on_thumb_leave)
		
	def draw_thumb(self, pos, color):
		if self.orient == "vertical":
			self.create_rectangle(
				0, pos, 
				self.winfo_width(), 
				pos + self.thumb_size, 
				fill=color, 
				outline="", 
				tags="thumb"
			)
			
		else:
			self.create_rectangle(
				pos, 0,
				pos + self.thumb_size,
				self.winfo_height(),
				fill=color,
				outline="",
				tags="thumb"
			)
			
		self.tag_bind("thumb", "<Enter>", self.on_thumb_hover)
		self.tag_bind("thumb", "<Leave>", self.on_thumb_leave)
		
	def draw_gradient_scroll(self, pos):
		steps = 60
		offset = self.anim_offset
		
		for i in range(steps):
			ratio = ((i + offset) % steps) / (steps - 1)
			r, b, g = self.interpolate_colors(ratio)
			color = f'#{r:02x}{g:02x}{b:02x}'
			
			if self.orient == "vertical":
					y = pos + (self.thumb_size * i / steps)
					self.create_rectangle(0, y, self.winfo_width(), y + self.thumb_size / steps, fill=color, outline="", tags="thumb")
			
			else:
				x = pos + (self.thumb_size * i / steps)
				self.create_rectangle(x, 0, x + self.thumb_size / steps, self.winfo_height(), fill=color, outline="", tags="thumb")
				
	def draw_gradient_pulse(self, pos):
		base = self.options["gradient_thumb"][0]
		pulse = self.pulse_strength
		r = int(min(255, base[0] + pulse * 50))
		g = int(min(255, base[1] + pulse * 50))
		b = int(min(255, base[2] + pulse * 50))
		color = f"#{r:02x}{g:02x}{b:02x}"
		self.draw_thumb(pos, color)
		
	def draw_shimmer(self, pos):
		base = self.options["gradient_thumb"][0]
		highlight = (255, 255, 255)
		stripe = self.anim_offset
		
		for i in range(int(self.thumb_size)):
			blend = max(0, 1 - abs(i - stripe) / 10)
			r = int(base[0] + (highlight[0] - base[0]) * blend)
			g = int(base[1] + (highlight[1] - base[1]) * blend)
			b = int(base[2] + (highlight[2] - base[2]) * blend)
			color = f"#{r:02x}{g:02x}{b:02x}"
			
			if self.orient == "vertical":
				y = pos + i
				self.create_line(0, y, self.winfo_width(), y, fill=color, tags="thumb")
				
			else:
				x = pos + i
				self.create_line(x, 0, x, self.winfo_height(), fill=color, tags="thumb")
		
	def animate(self):
		self.anim_offset = (self.anim_offset + 1) % int(self.thumb_size + 20)
		
		if self.options["animation"] == "pulse":
			self.pulse_strength += 0.05 * self.pulse_direction
			if self.pulse_strength >= 1.0 or self.pulse_strength <= 0.0:
				self.pulse_direction *= -1
				self.pulse_strength = max(0.0, min(1.0, self.pulse_strength))
				
		self.redraw()
		self.after(50, self.animate)
		
	def interpolate_colors(self, t):
		stops = self.options["gradient_thumb"]
		
		n = len(stops) - 1
		
		if n <= 0:
			return stops[0]
			
		seg = min(int(t * n), n - 1)
		local_t = (t * n) - seg
		r0, g0, b0 = stops[seg]
		r1, g1, b1 = stops[seg + 1]
		r = int(r0 + (r1 - r0) * local_t)
		g = int(g0 + (g1 - g0) * local_t)
		b = int(b0 + (b1 - b0) * local_t)
		return r,g,b
		
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
		if not self.options["animation"]:
			self.itemconfig("thumb", fill=self.options.get("thumb_hover_color", "#666666"))
		
	def on_thumb_leave(self, event=None):
		self.hovering = False
		if not self.dragging and not self.options["animation"]:
			self.itemconfig("thumb", fill=self.options.get("thumb_color", "#888888"))
		
	def on_release(self, event=None):	
		self.dragging = False
		if not self.hovering and not self.options["animation"]:
			self.itemconfig("thumb", fill=self.options.get("thumb_color", "#888888"))