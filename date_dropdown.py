from tkinter import Canvas, StringVar, Tk, Toplevel, Listbox, Frame, font as tkfont
from datetime import datetime
import calendar
from tkwidgets.scrollbar import TkScrollbar

class TkDateDropdown(Canvas):
	def __init__(self, parent, min_year=None, max_year=None, command=None, scrollbar_options=None, listbox_options=None, **kwargs):
		self.options = {
			"width": 210,
			"height": 30,
			"font": ("Arial", 12),
			"fg": "#000",
			"bg": "white",
			"border_color": "#888",
			"border_thickness": 2,
			"triangle_color": "#444",
			"triangle_size": 5,
			"triangle_scale": False,
			"triangle_padding": 10,
			"hover_bg": "#f0f0f0",
			"disabled_fg": "#999",
			"disabled_bg": "#ddd",
			"entry_hover_bg": "#e0e0e0",
			"active_border_color": "#0078D7",
			"entry_spacing": 5,
			"date_format": "%Y-%m-%d",
		}
		self.options.update(kwargs)
		
		self.no_past_dates = kwargs.get("no_past_dates", False)
		
		self.scrollbar_options = {
			"bg": self.options["bg"],
			**(scrollbar_options or {})
		}
		
		self.listbox_options = {
			"bg": self.options["bg"],
			"fg": self.options["fg"],
			"font": self.options["font"],
			"borderwidth": 0,
			"relief": "flat",
			**(listbox_options or {})
		}
		
		super().__init__(
			parent,
			width=self.options["width"],
			height=self.options["height"],
			bg=self.options["bg"],
			highlightthickness=0,
		)
		
		today = datetime.today()
		self.min_year = max(min_year if min_year is not None else today.year, today.year)
		self.max_year = max_year if max_year is not None else today.year + 100
		self.command = command
		self.state="normal"
		
		self.year_var = StringVar(value=str(today.year))
		self.month_var = StringVar(value=str(today.month))
		self.day_var = StringVar(value=str(today.day))
		
		self.dropdown = None
		self.last_listbox = None
		self.scrollbar = None
		self.hover_index = None
		self.active_index = None
		self._last_dropdown_index = None
		self._last_dropdown_coords = None
		
		self.bind("<Button-1>", self._on_click)
		self.bind("<Configure>", self._draw_entries)
		self.bind("<Motion>", self._on_motion)
		self.bind("<Leave>", self._on_leave)
		
		self.winfo_toplevel().bind("<Configure>", self._on_root_move)
		self.winfo_toplevel().bind("<Button-1>", self._on_global_click, add="+")
		
	def _on_click(self, event):
		for i, (x1, y1, x2, y2) in enumerate(self.entry_boxes):
			if x1 <= event.x <= x2 and y1 <= event.y <= y2:
				self.active_index = i
				x = x1
				y = self.winfo_height()
				self._show_dropdown(i, x, y)
				break
				
	def _show_dropdown(self, index, x, y):
		if self.dropdown:
			self.dropdown.destroy()
			
		self.dropdown = Toplevel(self)
		self.dropdown.overrideredirect(True)
		self.dropdown.geometry(f"{self.entry_width}x100+{self.winfo_rootx() + x}+{self.winfo_rooty() + y}")
		self._last_dropdown_coords = (x, y)
		
		frame = Frame(self.dropdown)
		frame.pack(fill="both", expand=True)
		
		sb = TkScrollbar(frame, orient="vertical", **self.scrollbar_options)
		sb.pack(side="right", fill="y")
		
		lb = Listbox(frame, **self.listbox_options)
		lb.pack(side="left", fill="both", expand=True)
		
		self.dropdown.update_idletasks()
		
		lb.config(yscrollcommand=sb.set)
		sb.command= lb.yview
		
		today = datetime.today()
		
		if index == 0: #Month
			values = list(range(1, 13))
			
		elif index == 1: #Day
			year = int(self.year_var.get())
			
			month = int(self.month_var.get())
			_, max_day = calendar.monthrange(year, month)
			values = list(range(1, max_day + 1))
			
		else: #Year
			values = list(range(self.min_year, self.max_year + 1))
			
		for val in values:
			try:
				if index == 0:
					d = datetime(int(self.year_var.get()), int(val), int(self.day_var.get()))
					
				elif index == 1:
					d = datetime(int(self.year_var.get()), int(self.month_var.get()), int(val))
					
				else:
					d = datetime(int(val), int(self.month_var.get()), int(self.day_var.get()))
					
				if self.no_past_dates and d.date() < today.date():
					continue
					
				lb.insert("end", str(val))
			
			except ValueError:
				continue
				
		def on_select(evt):
			selected = lb.curselection()
			
			if selected:
				val = lb.get(selected[0])
				
				if index == 0:
					self.month_var.set(val)
					
				elif index == 1:
					self.day_var.set(val)
					
				else:
					self.year_var.set(val)
					
				self.dropdown.destroy()
				self.dropdown = None
				self.active_index = None
				self._draw_entries()
				if self.command:
					self.command(self.get())
					
		lb.bind("<ButtonRelease-1>", on_select)
		
	def _on_global_click(self, event):
		if self.dropdown and not self.dropdown.winfo_containing(event.x_root, event.y_root):
			self.dropdown.destroy()
			self.dropdown = None
			self.active_index = None
			self._draw_entries()
			
	def _on_motion(self, event):
		self.hover_index = None
		
		for i, (x1, y1, x2, y2) in enumerate(self.entry_boxes):
			if x1 <= event.x <= x2 and y1 <= event.y <= y2:
				self.hover_index = i
				break
				
	def _on_leave(self, event):
		self.hover_index = None
		self._draw_entries()
		
	def _on_root_move(self, event):
		if self.dropdown and self._last_dropdown_coords:
			x, y = self._last_dropdown_coords
			abs_x = self.winfo_rootx() + x
			abs_y = self.winfo_rooty() + y
			self.dropdown.geometry(f"{self.entry_width}x100+{abs_x}+{abs_y}")
			
	def _draw_entries(self, event=None):
		self.delete("all")
		
		font_obj = tkfont.Font(font=self.options["font"])
		text_height = font_obj.metrics("linespace")
		min_height = text_height + self.options["border_thickness"] * 2 + 4
		h = max(self.options["height"], min_height)
		self.configure(height=h)
		
		w = self.winfo_width()
		spacing = self.options["entry_spacing"]
		total_spacing = spacing * 2
		
		triangle_pad = self.options["triangle_padding"]
		min_entry_width = font_obj.measure("88") + triangle_pad * 2
		self.entry_width = max(min_entry_width, (w - total_spacing) // 3)
		
		total_width = self.entry_width * 3 + total_spacing
		if w < total_width:
			self.configure(width=total_width)
			w = total_width
			
		self.entry_boxes = []
		bg_color = self.options["bg"]
		
		self.create_rectangle(0, 0, w, h, fill=bg_color, outline="")
		
		x_positions = [0, self.entry_width + spacing, 2 * (self.entry_width + spacing)]
		vars = [self.month_var, self.day_var, self.year_var]
		
		for i, x in enumerate(x_positions):
			self.entry_boxes.append((x, 0, x + self.entry_width, h))
			
			is_hover = self.hover_index == i and self.state == "normal"
			border_color = self.options["active_border_color"] if self.active_index == i else self.options["border_color"]
			hover_bg = self.options["entry_hover_bg"] if is_hover else bg_color
			fill_color = self.options["disabled_bg"] if self.state == "disabled" else hover_bg
			
			self.create_rectangle(
				x, 0, x + self.entry_width, h,
				outline=border_color,
				width=self.options["border_thickness"],
				fill=fill_color,
			)
			
			self.create_text(
				x + 8, h // 2,
				anchor="w",
				text=vars[i].get().zfill(2) if i != 2 else vars[i].get(),
				fill=self.options["disabled_fg"] if self.state == "disabled" else self.options["fg"],
				font=self.options["font"],
			)
			
			tx = x + self.entry_width - triangle_pad
			ty = h // 2
			
			size = int(text_height * .5) if self.options.get("triangle_scale", False) else self.options["triangle_size"]
			half_width = size
			half_height = int(size * .6)
			
			self.create_polygon(
				tx - half_width, ty - half_height,
				tx + half_width, ty - half_height,
				tx, ty + half_height,
				fill=self.options["triangle_color"] if self.state == "normal" else self.options["disabled_fg"],
				outline="",
			)
	def set(self, date_str):
		try:
			dt = datetime.strptime(date_str, self.options["date_format"])
			
			if self.no_past_dates and dt.date() < datetime.today().date():
				return
				
			self.year_var.set(str(dt.year))
			self.month_var.set(str(dt.month))
			self.day_var.set(str(dt.day))
			self._draw_entries()
			
		except ValueError:
			pass
			
	def get(self):
		try:
			date_obj = datetime(
				int(self.year_var.get()),
				int(self.month_var.get()),
				int(self.day_var.get()),
			)
			
			return date_obj.strftime(self.options["date_format"])
		
		except ValueError:
			return ""
		
	def disable(self):
		self.state = "disabled"
		
		self._draw_entries()
		
	def enable(self):
		self.state = "normal"
		
		self._draw_entries()