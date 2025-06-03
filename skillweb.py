from tkinter import Canvas
import math

class TkSkillWeb(Canvas):
	def __init__(self, parent, skills, **kwargs):
		#Default Options
		self.options = {
			"outer_radius": 200,
			"inner_radius": 50,
			"layers": 5,
			"bg": "white",
			"outline_color": "black",
			"label_color": "black",
			"label_font": ("Arial", 10),
			"point_color": "black",
			"fill_color": "black",
			"label_offset": 20,
		}
		self.options.update(kwargs)
		
		super().__init__(parent, bg=self.options["bg"])
		
		self.skills = skills
		
		self.offset = -math.pi / 2
		
		self.bind("<Configure>", self.draw)
		
	def config(self, **kwargs):
		self.options.update(kwargs)
		
		if "bg" in kwargs:
			self.configure(bg=self.options["bg"])
			
		self.draw()
		
	def draw(self, event=None):
		self.delete("all")
		
		self.update_idletasks()
		
		self.center_x = self.winfo_width() / 2
		self.center_y = self.winfo_height() / 2
		
		self.draw_layers()
		self.draw_skill_shape()
		
	def draw_layers(self):
		skill_names = list(self.skills.keys())
		
		self.n_gon = len(skill_names)
		
		angle_step = 2 * math.pi / self.n_gon
		
		decrement = (self.options["outer_radius"] - self.options["inner_radius"]) / (self.options["layers"] - 1)
		
		for layer in range(self.options["layers"]):
			radius = self.options["outer_radius"] - layer * decrement
			vertices = []
			
			for i in range(self.n_gon):
				angle = self.offset + i * angle_step
				
				x = self.center_x + radius * math.cos(angle)
				y = self.center_y + radius * math.sin(angle)
				
				vertices.append((x, y))
				
			self.create_polygon(vertices, fill="", outline=self.options["outline_color"], width=2)
			
			if layer == 0:
				for i, (x, y) in enumerate(vertices):
					self.create_line(x, y, self.center_x, self.center_y, fill=self.options["outline_color"], width=2)
					
					label_radius = self.options["outer_radius"] + self.options["label_offset"]
					
					angle = self.offset + i * angle_step
					
					lbl_x = self.center_x + label_radius * math.cos(angle)
					lbl_y = self.center_y + label_radius * math.sin(angle)
					
					self.create_text(lbl_x, lbl_y, text=skill_names[i], fill=self.options["label_color"], font=self.options["label_font"])
					
	def draw_skill_shape(self):
		skill_values = list(self.skills.values())
		
		angle_step = 2 * math.pi / len(skill_values)
		
		points = []
		
		for i, value in enumerate(skill_values):
			normalized = max(0, min(value, 100)) / 100
			
			radius = self.options["inner_radius"] + normalized * (self.options["outer_radius"] - self.options["inner_radius"])
			
			angle = self.offset + i * angle_step
			
			x = self.center_x + radius * math.cos(angle)
			y = self.center_y + radius * math.sin(angle)
			
			points.append((x, y))
			
		self.create_polygon(points, fill=self.options["fill_color"], outline=self.options["outline_color"], width=2)
		
		for x, y in points:
			self.create_oval(x - 6, y - 6, x + 6, y + 6, fill=self.options["point_color"], outline=self.options["outline_color"], width=2)