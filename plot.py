from mcpi import minecraft
from block import *
from brush import *
from patterns import *
from utils import *
from fast_query import *

from building import Building
from yard import Yard
from decoration import Garden

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from village import Village

SEARCH_ATTEMPTS_BEFORE_EXPANDING = 1000
INVALID_STARTER_BLOCKS 	= [WATER_FLOWING, LAVA_FLOWING, LAVA_STATIONARY, WATER_STATIONARY] # took ice out because i wanna try an ice city
VILLAGE_BOUNDARY_EXCLUSION = 4	# don't put plots right on the edge of the village area in case we need to path there

SPECIAL_BUILDINGS = {
	'fountain':	{
		'name': 'the village fountain',
		'pattern': FOUNTAIN_13x13,
		'size':	 Vector2(13, 13),
		'requires_path': True,
		'base_height_offset': 0,
		'repeatable': False
	},
	'farm_wheat':	{
		'name': 'a large wheat farm',
		'pattern': FARM_WHEAT_21x11,
		'size':	 Vector2(21, 11),
		'requires_path': True,
		'base_height_offset': 0,
		'repeatable': False
	},
	'farm_carrot':	{
		'name': 'a small carrot farm',
		'pattern': FARM_CARROT_11x11,
		'size':	 Vector2(11, 11),
		'requires_path': True,
		'base_height_offset': 0,
		'repeatable': False
	},
	'farm_beet':	{
		'name': 'a small beetroot farm',
		'pattern': FARM_BEET_11x11,
		'size':	 Vector2(11, 11),
		'requires_path': True,
		'base_height_offset': 0,
		'repeatable': False
	},
	'tall_tree':	{
		'name': 'a tall tree',
		'pattern': TALL_TREE,
		'size':	 Vector2(8, 9),
		'requires_path': False,
		'base_height_offset': 0,
		'repeatable': True
	},
	'tall_tree':	{
		'name': 'a small tree',
		'pattern': SMALL_TREE,
		'size':	 Vector2(5, 5),
		'requires_path': False,
		'base_height_offset': 0,
		'repeatable': True
	},
	'well':	{
		'name': 'the village well',
		'pattern': WELL,
		'size':	 Vector2(6, 7),
		'requires_path': True,
		'base_height_offset': -4,
		'repeatable': False
	},
	'garden': {
		'name': 'a garden plot',
		'pattern': None,
		'class': Garden,
		'size': Vector2(10, 13),
		'requires_path': False,
		'base_height_offset': 1,
		'repeatable': True
	}
}

class Plot:
	def __init__(self, mc : minecraft.Minecraft, village : 'Village', building=True):

		self.mc = mc
		self.village = village
		self.name = 'Unnamed structure'

		self.base_height : int = None
		self.foundation_rect : Rectangle = None
		self.requires_path = True

		if building:
			house_adjectives = [' lovely', ' splendid', ' quaint', ' pleasant', ' nice', ' cozy', ' charming', ' dear little', ' special', ' wonderful', ' smart little', ' brilliant', ' grand', ' little', ' welcoming', 'n inviting']
			house_nouns = [' house', ' home', ' cottage', ' shack']
			self.name = 'a' + random.choice(house_adjectives) + random.choice(house_nouns)
			foundation_width  = random.randrange(*self.village.plot_size_range.range()) 
			foundation_height = random.randrange(*self.village.plot_size_range.range())
			self.foundation_size = Vector2(foundation_width, foundation_height)

			self.lawn_size: Vector2 = Vector2(random.randrange(3,5), random.randrange(3,5))
			self.lawn_offset: Vector2 = Vector2(0, 0) # disabled - needs adjustments to pathing to make this stable.
		else:
			special_building_key = random.choice(list(SPECIAL_BUILDINGS))
			special_building = SPECIAL_BUILDINGS[special_building_key]

			self.name = special_building['name']
			self.foundation_size = special_building['size']
			self.requires_path = special_building['requires_path']
			self.pattern = special_building['pattern']
			# last minute addition to get the non-pattern decorations generating in plots
			if self.pattern == None:
				self.decoration_class = special_building['class']

			self.bh_offset = special_building['base_height_offset']

			self.lawn_size = Vector2(1, 1)
			self.lawn_offset = Vector2(0, 0)
			
			if special_building['repeatable'] == False:
				del SPECIAL_BUILDINGS[special_building_key]
		
		self.find_plot_location()
		# self.village.map.level(self.flat_area().expanded_by(2), self.base_height)
		self.village.map.level(self.flat_area().expanded_by(2), self.base_height)
		self.mc.postToChat(f'Smoothing terrain {self.terraform_area()}.')
		self.village.map.blur5x5(self.terraform_area(), self.flat_area(), self.village.plot_smooth_iterations)
		# self.village.map.validate_map_keys()	# looking for cause of key error, but i think it's the server failing to provide block data in time

		if building:
			self.building = Building(self.mc, self.foundation_rect, self.base_height)
			self.yard = Yard(self.mc, self, self.flat_area(), self.foundation_rect, self.base_height)
			# mark lawn and house as no-go areas for pathing (except for a strip to get to the door)
			self.door_mat, door_facing = self.building.get_doormat()
			door_path = Rectangle(self.door_mat, self.door_mat + (door_facing * self.lawn_size))
			self.village.map.forbid(self.flat_area().expanded_by(-1), door_path, CUSTOM_LAWN)
			self.village.map.forbid(self.foundation_rect, door_path, CUSTOM_BUILDING)
		else:
			# village decorations
			self.door_mat = Vector2(self.foundation_rect.x0 + self.foundation_rect.width // 2, self.foundation_rect.z0)
			# randomly put the doormat on the north or south. could do all 4 dirs, but pressed for time. :(
			door_facing = random.choice([Vector2(0, -1), Vector2(0, 1)])
			door_path = Rectangle(self.door_mat, self.door_mat + (door_facing * (self.foundation_size.z // 2)))
			self.village.map.forbid(self.flat_area().expanded_by(-1), door_path, CUSTOM_LAWN)
			self.village.map.forbid(self.foundation_rect, door_path, CUSTOM_BUILDING)
			if self.pattern:
				b = Brush(self.mc, Pattern(self.pattern))
				b.face(Facing.SOUTH)
				b.draw(self.foundation_rect.x0, self.base_height + self.bh_offset, self.foundation_rect.z0, self.foundation_rect.x0 + self.foundation_size.x - 1,  self.base_height + self.bh_offset, self.foundation_rect.z0)
			else:
				self.decoration_class(self.mc, Vector3(self.foundation_rect.x0, self.base_height, self.foundation_rect.z0), Vector3(self.foundation_rect.x1, self.base_height, self.foundation_rect.z1))

		self.mc.postToChat(f'Built {self}')

	def __str__(self) -> str:
		return f'{self.name}: {self.foundation_rect} at height {self.base_height}, with lawn {self.lawn_size}, blur border {self.village.plot_smooth_border}.'

	def __repr__(self) -> str:
		return self.str()

	def debug_draw(self, mc : minecraft.Minecraft):
		# need to draw building footprint, lawn/yard area, blur area
		self.mc.setBlocks(self.flat_area().x0, self.village.DEBUG_DRAW_HEIGHT + 5, self.flat_area().z0, self.flat_area().x1, self.village.DEBUG_DRAW_HEIGHT + 5, self.flat_area().z1, GLASS)
		self.mc.setBlocks(self.foundation_rect.x0,  self.village.DEBUG_DRAW_HEIGHT + 4, self.foundation_rect.z0, self.foundation_rect.x1,  self.village.DEBUG_DRAW_HEIGHT + 4, self.foundation_rect.z1, END_STONE)
		self.mc.setBlocks(self.terraform_area().x0, self.village.DEBUG_DRAW_HEIGHT + 3, self.terraform_area().z0, self.terraform_area().x1, self.village.DEBUG_DRAW_HEIGHT + 3, self.terraform_area().z1, EMERALD_ORE)

	###	PLOT BOUNDARIES

	def	flat_area(self) -> Rectangle:
		return self.foundation_rect.expanded_by(self.lawn_size) + self.lawn_offset

	def terraform_area(self) -> Rectangle:
		return self.flat_area().expanded_by(self.village.plot_smooth_border)

	###	FIND PLOT

	def find_plot_location(self):
		# select random point from village height map
		possible_location = self.village.map.random_point()

		search_attempts = 0

		def valid_plot_location(hm_data : tuple[(int, int), (int, Block)]):

			if hm_data[1] is None:	# the heightmap filter marked this as no good, i.e. water, extreme height variation
				self.mc.postToChat('plot.valid_plot_location(), HEIGHTMAP DATA WAS NONE?')
				return False

			x, z = hm_data[0]
			y, blk = hm_data[1]

			if blk in INVALID_STARTER_BLOCKS:
				return False

			self.foundation_rect = Vector2(x, z).extended_by(self.foundation_size)
			# offset it, so it's centred on the randomly chosen starter block
			self.foundation_rect += Vector2(self.foundation_rect.width // 2, self.foundation_rect.height // 2)

			if not self.village.bounds.contains(self.terraform_area().expanded_by(VILLAGE_BOUNDARY_EXCLUSION)):
				return False

			if any(plot.flat_area().intersects(self.terraform_area()) for plot in self.village.plots):
				return False

			self.base_height = self.village.map.sample(self.foundation_rect)

			# check if any of the plot is on water, etc.
			for x in range(*self.flat_area().x_range()):
				for z in range(*self.flat_area().z_range()):
					if not (x, z) in self.village.map._map:	# fail if the plot is partly out of bounds
						print(f'KEY {x}, {z} not in dictionary (bounds {self.village.bounds}).')
						return False
					if self.village.map.block(x, z) in INVALID_STARTER_BLOCKS:
						return False

			return True

		while not valid_plot_location(possible_location):
			if search_attempts > SEARCH_ATTEMPTS_BEFORE_EXPANDING:
				self.mc.postToChat('Could not find suitable plot location...')
				self.village.expand_bounds()
				search_attempts = 0
			
			possible_location = self.village.map.random_point()

			search_attempts += 1
		else:
			self.mc.postToChat(f'Plot location found: {self.foundation_rect}')

if __name__ == "__main__":
	# try:
	# 	mc = minecraft.Minecraft.create()
	# 	plotter = Plot(mc)
	# except socket.error as e:
	# 	print("Cannot connect to Minecraft server")
	# 	raise e
	pass