from tkinter import Canvas

class TkTileMap(Canvas):
	def __init__(self, parent, **kwargs):
		#Default Options
		self.options = {
			"bg": "white",
			"tile_num": 11,
			"min_tiles": 11,
			"max_tiles": 51,
		}
		self.options.update(kwargs)
		
		super().__init__(
			parent,
			bg=self.options["bg"],
		)
		
		self.tile_num = self.options["tile_num"]
		self.min_tiles = self.options["min_tiles"]
		self.max_tiles = self.options["max_tiles"]
		
		self.tiles = []
		self.color_grid = None
		
		self.bind("<Configure>", self.draw_map)
		self.bind("<MouseWheel>", self.on_mousewheel)
		self.bind("<Button-4>", self.on_mousewheel) # Linux Up
		self.bind("<Button-5>", self.on_mousewheel) # Linux Down
		
	def config(self, **kwargs):
		self.options.update(kwargs)
		
		if "bg" in kwargs:
			self.configure(bg=self.options["bg"])
		
	def set_color_grid(self, grid):
		size = len(grid)
		
		if any(len(row) != size for row in grid):
			raise ValueError("Color grid size must equal current tile_num")
			
		self.color_grid = grid	
			
		if size != self.tile_num or len(self.tiles) != size:
			self.tile_num = size
			self.draw_map()
			return
		
		for r in range(size):
			row_tiles = self.tiles[r]
			row_colors = grid[r]
			
			for c in range(size):
				self.itemconfig(row_tiles[c], fill=row_colors[c])
				
	def set_tile(self, row, col, color):	
		self.itemconfig(self.tiles[row][col], fill=color)
		
		if self.color_grid:
			self.color_grid[row][col] = color
		
	def draw_map(self, event=None):
		self.update_idletasks()
		
		width = self.winfo_width()
		height = self.winfo_height()
		
		tile_width = width / self.tile_num
		tile_height = height / self.tile_num
		
		half = self.tile_num // 2
		
		self.delete("map")
		
		self.tiles = []
		
		for row in range(self.tile_num):
			row_ids = []
			
			for col in range(self.tile_num):
				x0 = col * tile_width
				y0 = row * tile_height
				
				x1 = x0 + tile_width
				y1 = y0 + tile_height
				
				id = self.create_rectangle(
					x0, y0,
					x1, y1,
					tags="map",
				)
				
				row_ids.append(id)
				
			self.tiles.append(row_ids)
			
		self.apply_color_grid()
		
	def apply_color_grid(self):
		if self.color_grid and len(self.color_grid) == self.tile_num and all(len(row) == self.tile_num for row in self.color_grid):
			for r in range(self.tile_num):
				row_tiles = self.tiles[r]
				row_colors = self.color_grid[r]
				for c in range(self.tile_num):
					self.itemconfig(row_tiles[c], fill=row_colors[c])
				
	def on_mousewheel(self, event):
		if event.delta:
			direction = 1 if event.delta > 0 else -1
			
		else:
			direction = 1 if event.num == 4 else -1
			
		old = self.tile_num
		
		if direction > 0 and self.tile_num > self.min_tiles:
			self.tile_num -= 2
			
		elif direction < 0 and self.tile_num < self.max_tiles:
			self.tile_num += 2
			
		if self.tile_num != old:
			self.draw_map()
			
		return "break"