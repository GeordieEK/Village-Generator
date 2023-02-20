from turtle import up
from mcpi import minecraft
import block

from plot import *
from fast_query import *
from utils import *
from building import *
from heightmap import *

from brush import *
import socket
import random

VILLAGE_BOUNDS_INCREMENT = 30
DEBUG_DRAW_HEIGHT = 100

class Village:

	def __init__(self, mc: minecraft.Minecraft):
		self.mc = mc
		self.centre = mc.player.getTilePos()
		self.bounds = Rectangle(
			Vector2(self.centre.x - VILLAGE_BOUNDS_INCREMENT, self.centre.z - VILLAGE_BOUNDS_INCREMENT),
			Vector2(self.centre.x + VILLAGE_BOUNDS_INCREMENT, self.centre.z + VILLAGE_BOUNDS_INCREMENT))

		self.DEBUG_DRAW_HEIGHT = DEBUG_DRAW_HEIGHT
		self.mc.postToChat(f'Generating height map {self.bounds}.')
		self.map = Heightmap(self.mc, self.bounds)
		self.mc.postToChat('Height map complete.')
		
		# village generation parameters
		self.num_buildings = random.randrange(5, 10)
		self.num_special_buildings = random.randrange(3, 7)
		self.plot_smooth_border = random.randrange(4, 6)
		self.plot_smooth_iterations = 3
		self.plot_size_range = Vector2(5, 20)

		self.plots = []

	def construct(self):
		for _ in range(0, self.num_buildings):
			new_plot = Plot(self.mc, self)
			self.plots.append(new_plot)
		self.mc.postToChat('Houses constructed.')
		for _ in range(0, self.num_special_buildings):
			if SPECIAL_BUILDINGS:
				new_plot = Plot(self.mc, self, building=False)
				self.plots.append(new_plot)
		self.mc.postToChat('Additional structures constructed.')
		self.mc.postToChat("Building complete..")


	def expand_bounds(self, amount: int = VILLAGE_BOUNDS_INCREMENT, all_directions = False):
		if all_directions == False:
			direction = random.choice([Facing.NORTH, Facing.SOUTH, Facing.EAST, Facing.WEST])

			if direction is Facing.NORTH:
				self.mc.postToChat('Expanding village to north.')
				# important to update new area first, as it references old bounds
				new_area = 	  Rectangle(Vector2(self.bounds.x0, self.bounds.z0 - amount),
										Vector2(self.bounds.x1, self.bounds.z0))
				self.bounds = Rectangle(Vector2(self.bounds.x0, self.bounds.z0 - amount),
										Vector2(self.bounds.x1, self.bounds.z1))
			elif direction is Facing.SOUTH:
				self.mc.postToChat('Expanding village to south.')
				new_area =    Rectangle(Vector2(self.bounds.x0, self.bounds.z1),
										Vector2(self.bounds.x1, self.bounds.z1 + amount))
				self.bounds = Rectangle(Vector2(self.bounds.x0, self.bounds.z0),
										Vector2(self.bounds.x1, self.bounds.z1 + amount))
			elif direction is Facing.EAST:	# expand east
				self.mc.postToChat('Expanding village to east.')
				new_area =    Rectangle(Vector2(self.bounds.x1, self.bounds.z0),
										Vector2(self.bounds.x1 + amount, self.bounds.z1))
				self.bounds = Rectangle(Vector2(self.bounds.x0, self.bounds.z0),
										Vector2(self.bounds.x1 + amount, self.bounds.z1))
			else:	# expand west
				self.mc.postToChat('Expanding village to west.')
				new_area =    Rectangle(Vector2(self.bounds.x0 - amount, self.bounds.z0),
										Vector2(self.bounds.x0, self.bounds.z1))
				self.bounds = Rectangle(Vector2(self.bounds.x0 - amount, self.bounds.z0),
										Vector2(self.bounds.x1, self.bounds.z1))
		else:
			new_area = self.bounds.expanded_by(amount)
			self.bounds = new_area

		self.map.update_bounds(new_area, self.bounds)
		self.mc.postToChat(f'New bounds are {self.bounds}.')

	def debug_draw(self):
		# mark the village centre
		self.mc.setBlock(self.centre.x, DEBUG_DRAW_HEIGHT + 10, self.centre.z, block.DIAMOND_BLOCK)
		self.mc.setBlock(self.centre.x, DEBUG_DRAW_HEIGHT + 11, self.centre.z, block.DIAMOND_BLOCK)
		self.mc.setBlock(self.centre.x, DEBUG_DRAW_HEIGHT + 12, self.centre.z, block.DIAMOND_BLOCK)
		# mark the village bounds
		Brush.draw_rect(self.mc,
						self.bounds.small_corner.asX_Z(DEBUG_DRAW_HEIGHT + 10),
						self.bounds.large_corner.asX_Z(DEBUG_DRAW_HEIGHT + 10),
						block.GOLD_BLOCK)
		# mark plot bounds
		for plot in self.plots:
			plot.debug_draw(self.mc)

				
if __name__ == "__main__":
	try:
		mc = minecraft.Minecraft.create()
	except socket.error as e:
		print("Cannot connect to Minecraft server")
		raise e

	if True:
		a_lovely_village = Village(mc)
		a_lovely_village.construct()
	# a_lovely_village.debug_draw()

	if False:
		for plot in a_lovely_village.plots:
			location = plot.building.door_coords
			print(location)
	# village pathing test
	if False:
		# General setup
		a_lovely_village = Village(mc)
		a_lovely_village.construct()

		px, py, pz = a_lovely_village.centre
		sz = 70

		test_cuboid = Cuboid((px - sz, px + sz + 1), (0, 1), (pz - sz, pz + sz + 1))
		hm = fq_heights_and_surface_id_filtered(test_cuboid)
		mc.postToChat("Map created.")

		door_locations = []
		for plot in a_lovely_village.plots:
			door_coords = Vector3(plot.building.get_door_coords()[0], plot.building.get_door_coords()[1],
								  plot.building.get_door_coords()[2])
			door_coords_to_append = (door_coords.x, door_coords.z)
			door_locations.append(door_coords_to_append)
			print(door_coords_to_append)
			mc.postToChat("door location added:")
			mc.postToChat(door_coords_to_append)

		current_location = door_locations.pop()
		while len(door_locations):
			next = door_locations.pop()
			path_finder(current_location, next, hm, mc)

	if False:
		position = mc.player.getTilePos()
		top_left = Vector3(position.x - 10, position.y, position.z - 10)
		bottom_right = Vector3(position.x + 10, position.y, position.z + 10)
		building = Building(mc, top_left, bottom_right, 4)
		print(building.door_location)
