from utils import *
import random
from fast_query import *
from block import *

APPLY_BELOW_SURFACE_PATTERN = [DIRT, DIRT, DIRT, DIRT, DIRT, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE]
DO_NOT_ALTER = [WATER_FLOWING, WATER_STATIONARY, LAVA_FLOWING, LAVA_STATIONARY]

class Heightmap:
	"""
	Map with height and optional block data.
	"""
	### CLASS METHODS


	### INSTANCE METHODS

	def __init__(self, mc: minecraft.Minecraft, bounds: Rectangle):
		"""		
		Parameters:
		rect: a bounding rectangle (world co-ordinates) for the height map.
		"""
		self.mc = mc
		self._map = None		# hmap: dict[(int, int), (int, Block)],
		self.bounds = bounds
		self.update_bounds(self.bounds, self.bounds)

	def print_values(self):
		for z in range(*self.bounds.z_range):
			s = ''
			for x in range(*self.bounds.x_range):
				s += f'{self._map[x, z]:^4}'
			print(s)

	def print_ascii(self, detailed : bool = False):
		"""
		Renders an ASCII image of the heightmap for debugging purposes.
		"""
		min_height = self._map[min(self._map, key=lambda k: self._map[k][0])][0]
		max_height = self._map[max(self._map, key=lambda k: self._map[k][0])][0]
		# min_height = hmap[min(hmap, key=hmap.get)]
		# max_height = hmap[max(hmap, key=hmap.get)]
		height_range = max_height - min_height

		GRADIENT = ' .:-=+*#%@'
		if detailed:
			GRADIENT = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1[]?-_+~<>i!lI;:,"^`. '[::-1]
			
		scaling = len(GRADIENT)/height_range

		for z in range(*self.bounds.z_range()):
			s = ""
			for x in range(*self.bounds.x_range()):
				y = self._map[x,z][0]
				c = '{:2}'.format(GRADIENT[int((y - min_height - 1) * scaling)])
				s = s + c
			print(s)

	def debug(self, block_types: list[Block], as_block: Block = GOLD_BLOCK, height: int = 127):
		for x in range(*self.bounds.x_range()):
			for z in range(*self.bounds.z_range()):
				blk = self._map[x, z][1]
				if blk in block_types:
					self.mc.setBlock(x, height, z, as_block.id, as_block.data)

	def validate_map_keys(self):
		for x in range(self.bounds.x0, self.bounds.x1):
			for z in range(self.bounds.z0, self.bounds.z1):
				if not (x, z) in self._map:
					print(f'Missing key: {x}, {z}')

	def update_bounds(self, area_to_add: Rectangle, new_bounds: Rectangle):
		"""
		Sets the new bounds for the map and requeries the height/block data, but only for the new area.
		Parameters:
		area_to_add: a Rectangle representing the new area of the map. Must be adjacent to the existing bounds.
		new_bounds:	 a Rectangle describing the total area covered by existing bounds + area_to_add.
					 Existing and area_to_add must be a partition of new_bounds - there cannot be x,z co-ords in new_bounds
					 that are not in one of existing and area_to_add.
		"""
		self.bounds = new_bounds
		new_data = fq_heights_and_surface_id_filtered(
			Cuboid(area_to_add.x_range(), (0, 1), area_to_add.z_range()))
		if self._map:
			self.mc.postToChat(f'Combining existing and new ({area_to_add}) heightmaps.')
			self._map.update(new_data)
		else:
			self._map = new_data

	def random_point(self):
		"""
		Returns a tuple of ((x, z), (y, Block)) from a random point in the map.
		"""
		return random.choice(list(self._map.items()))

	def sample(self, rect: Rectangle):
		"""
		Returns the most common height across the sampled area.
		"""
		frequencies = {}
		for x in range(rect.x0, rect.x1):
			for z in range(rect.z0, rect.z1):
				y = self.height(x, z)
				if y not in frequencies:
					frequencies[y] = 1
				else:
					frequencies[y] += 1
		return max(frequencies, key=frequencies.get)

	def	contains(self, point: Vector2) -> bool:
		"""
		Returns true if the point is within or on the bounds of the map.
		Parameters:
		point: a Vector2 to test.
		"""
		return self.bounds.contains(point)

	def forbid(self, forbidden_rect: Rectangle, mask_rect: Rectangle, custom_block: Block):
		for x in range(forbidden_rect.x0, forbidden_rect.x1 + 1):
			for z in range(forbidden_rect.z0, forbidden_rect.z1 + 1):
				if mask_rect and not mask_rect.contains(Vector2(x, z)):
					y, _ = self._map[x, z]
					self._map[x, z] = (y, custom_block)

	def apply(self, rect: Rectangle, mask_rect: Rectangle = None, mask_blocks: list[Block] = None):
		if mask_blocks is None:
			mask_blocks = []

		for x in range(*rect.x_range()):
			for z in range(*rect.z_range()):
				y, blk = self._map[x, z]
				if blk not in mask_blocks or (mask_rect and not mask_rect.contains(Vector2(x, z))):		#	FIXME	naive approach for time being
					#	first clear above
					self.mc.setBlocks(x, y + 1, z, x, 255, z, AIR)
					#	set the surface block
					self.mc.setBlocks(x, y, z, x, y, z, blk.id, blk.data)
					#	and set below
					y -= 1
					for blck in APPLY_BELOW_SURFACE_PATTERN:
						self.mc.setBlocks(x, y, z, x, y, z, blck.id)
						y -= 1

	def level(self, level_rect: Rectangle, height: int):
		"""
		Sets all blocks within level_rect to the specified height and then
		applies to the world.
		"""
		for x in range(*level_rect.x_range()):
			for z in range(*level_rect.z_range()):
				_, blk = self._map[x, z]
				self._map[x, z] = (height, blk)
		
		self.apply(level_rect)

	def border(self, border_rect: Rectangle, height: int):
		"""
		Sets the height along the edges of a levelled rect.

		Parameters
		border_rect: the border will be placed on the edges of this rect.
		height: the height of the border.
		"""
		for x in range(border_rect.x0, border_rect.x1):
				current_height, blk = self._map[x, border_rect.z0]
				new_height = current_height + (height - current_height) / 2
				self._map[x, border_rect.z0] = (new_height, blk)

				current_height, blk = self._map[x, border_rect.z1 - 1]
				new_height = current_height + (height - current_height) / 2
				self._map[x, border_rect.z1 - 1] = (new_height, blk)

		for z in range(border_rect.z0 + 1, border_rect.z1 - 1):
				current_height, blk = self._map[border_rect.x0, z]
				new_height = current_height + (height - current_height) / 2
				self._map[border_rect.x0, z] = (new_height, blk)

				current_height, blk = self._map[border_rect.x1, z]
				new_height = current_height + (height - current_height) / 2
				self._map[border_rect.x1 - 1, z] = (new_height, blk)

		self.apply(border_rect)

	def blur(self, blur_rect: Rectangle, mask_rect: Rectangle = None, iterations: int = 1):
		"""
		Applies a simple blur to the portion of the map specified by blur_rect and
		ignoring blocks in mask_rect.
		"""

								# TODO	might inline this to make it faster.
		blur_kernel = {			# assign weight to neighbouring directions
			(-1, -1): 1.0/16,	( 0, -1): 2.0/16,	(+1, -1): 1.0/16,
			(-1,  0): 2.0/16,	( 0,  0): 4.0/16,	(+1,  0): 2.0/16,
			(-1, +1): 1.0/16,	( 0, +1): 2.0/16,	(+1, +1): 1.0/16
		}

		for _ in range(iterations):
		
			temp_map = {}
		
			for x in range(*blur_rect.x_range()):
				for z in range(*blur_rect.z_range()):
					if mask_rect and mask_rect.contains(Vector2(x, z)):				# leave blocks in masked area alone
						temp_map[x, z] = self._map[x, z]
					else:
						#	if the neighbouring blocks are outside the height_map, then clamp them
						x_neg = (x - 1) if (x - 1) >= self.bounds.x0 else x
						x_pos = (x + 1) if (x + 1) < self.bounds.x1 else x
						z_neg = (z - 1) if (z - 1) >= self.bounds.z0 else z
						z_pos = (z + 1) if (z + 1) < self.bounds.z1 else z

						new_height = int(blur_kernel[(-1, -1)] * self._map[x_neg, z_neg][0] + 	\
										 blur_kernel[( 0, -1)] * self._map[x, 	  z_neg][0] +  	\
										 blur_kernel[(+1, -1)] * self._map[x_pos, z_neg][0] + 	\
																								\
										 blur_kernel[(-1,  0)] * self._map[x_neg, z	   ][0] + 	\
										 blur_kernel[( 0,  0)] * self._map[x,  	  z	   ][0] + 	\
										 blur_kernel[(+1,  0)] * self._map[x_pos, z	   ][0] +	\
																								\
										 blur_kernel[(-1, +1)] * self._map[x_neg, z_pos][0] +	\
										 blur_kernel[( 0, +1)] * self._map[x,	  z_pos][0] +	\
										 blur_kernel[(+1, +1)] * self._map[x_pos, z_pos][0])

						existing_block = self._map[x, z][1]	# get the existing block type from the height map
						temp_map[x, z] = (new_height, existing_block)
		
			# put the blurred data back into the original heightmap
			for k, v in temp_map.items():
				self._map[k] = v

		self.apply(blur_rect, mask_rect, mask_blocks = DO_NOT_ALTER)

	def blur5x5(self, blur_rect: Rectangle, mask_rect: Rectangle = None, iterations: int = 1):
		"""
		Applies a simple blur to the portion of the map specified by blur_rect and
		ignoring blocks in mask_rect.
		"""
		blur_kernel = {
			(-2, -2): 1.0/256,	(-1, -2): 4.0/256,	( 0, -2): 6.0/256,	(+1, -2): 4.0/256,	(+2, -2): 1.0/256,
			(-2, -1): 4.0/256,	(-1, -1):16.0/256,	( 0, -1):24.0/256,	(+1, -1):16.0/256,	(+2, -1): 4.0/256,
			(-2,  0): 6.0/256,	(-1,  0):24.0/256,	( 0,  0):36.0/256,	(+1,  0):24.0/256,	(+2,  0): 6.0/256,
			(-2, +1): 4.0/256,	(-1, +1):16.0/256,	( 0, +1):24.0/256,	(+1, +1):16.0/256,	(+2, +1): 4.0/256,
			(-2, +2): 1.0/256,	(-1, +2): 4.0/256,	( 0, +2): 6.0/256,	(+1, +2): 4.0/256,	(+2, +2): 1.0/256,
		}

		for _ in range(iterations):
		
			temp_map = {}
		
			for x in range(*blur_rect.x_range()):
				for z in range(*blur_rect.z_range()):
					if mask_rect and mask_rect.contains(Vector2(x, z)):				# leave blocks in masked area alone
						temp_map[x, z] = self._map[x, z]
					else:
						x_neg = (x - 1)
						x_neg2 = (x - 2)
						x_pos = (x + 1)
						x_pos2 = (x + 1)

						if x == self.bounds.x0:
							x_neg = x
							x_neg2 = x
						if x == self.bounds.x0 + 1:
							x_neg2 = x_neg
						if x == self.bounds.x1 - 1:
							x_pos = x
							x_pos2 = x
						if x == self.bounds.x1 - 2:
							x_pos2 = x_pos
							
						z_neg = (z - 1)
						z_neg2 = (z - 1)
						z_pos = (z + 1)
						z_pos2 = (z + 1)

						if z == self.bounds.z0:
							z_neg = z
							z_neg2 = z
						if z == self.bounds.z0 + 1:
							z_neg2 = z_neg
						if z == self.bounds.z1 - 1:
							z_pos = z
							z_pos2 = z
						if z == self.bounds.z1 - 2:
							z_pos2 = z_pos

						new_height = int(blur_kernel[(-2, -2)] * self._map[x_neg2, z_neg2][0] +
										 blur_kernel[(-1, -2)] * self._map[x_neg,  z_neg2][0] +
										 blur_kernel[( 0, -2)] * self._map[x, 	   z_neg2][0] +
										 blur_kernel[(+1, -2)] * self._map[x_pos,  z_neg2][0] +
										 blur_kernel[(+2, -2)] * self._map[x_pos2, z_neg2][0] +

										 blur_kernel[(-2, -1)] * self._map[x_neg2, z_neg][0] +
										 blur_kernel[(-1, -1)] * self._map[x_neg,  z_neg][0] +
										 blur_kernel[( 0, -1)] * self._map[x, 	   z_neg][0] +
										 blur_kernel[(+1, -1)] * self._map[x_pos,  z_neg][0] +
										 blur_kernel[(+2, -1)] * self._map[x_pos2, z_neg][0] +

										 blur_kernel[(-2,  0)] * self._map[x_neg2, z][0] +
										 blur_kernel[(-1,  0)] * self._map[x_neg,  z][0] +
										 blur_kernel[( 0,  0)] * self._map[x, 	   z][0] +
										 blur_kernel[(+1,  0)] * self._map[x_pos,  z][0] +
										 blur_kernel[(+2,  0)] * self._map[x_pos2, z][0] +

										 blur_kernel[(-2, +1)] * self._map[x_neg2, z_pos][0] +
										 blur_kernel[(-1, +1)] * self._map[x_neg,  z_pos][0] +
										 blur_kernel[( 0, +1)] * self._map[x, 	   z_pos][0] +
										 blur_kernel[(+1, +1)] * self._map[x_pos,  z_pos][0] +
										 blur_kernel[(+2, +1)] * self._map[x_pos2, z_pos][0] +

										 blur_kernel[(-2, +2)] * self._map[x_neg2, z_pos2][0] +
										 blur_kernel[(-1, +2)] * self._map[x_neg,  z_pos2][0] +
										 blur_kernel[( 0, +2)] * self._map[x, 	   z_pos2][0] +
										 blur_kernel[(+1, +2)] * self._map[x_pos,  z_pos2][0] +
										 blur_kernel[(+2, +2)] * self._map[x_pos2, z_pos2][0])

						existing_block = self._map[x, z][1]	# get the existing block type from the height map
						temp_map[x, z] = (new_height, existing_block)
		
			# put the blurred data back into the original heightmap
			for k, v in temp_map.items():
				self._map[k] = v

		self.apply(blur_rect, mask_rect, mask_blocks = DO_NOT_ALTER)

	def block(self, x: int, z: int) -> Block:
		return self._map[x, z][1]

	def height(self, x: int, z: int) -> int:
		try:
			h = self._map[x, z][0]
		except KeyError as k:
			print(f'KeyError: map bounds are {self.bounds}, requested key was ({x}, {z}).')
			print(f'RETURNING 65 as DEFAULT VALUE AS WORKAROUND.')
			return 65
		return h
		

	def height_block(self, x: int, z: int) -> int:
		return self._map[x, z]


### HEIGHTMAP BUILD FNS

#	TODO	move these into Heghtmap

def to_xyz(heightmap):
	for xz, y in heightmap.items():
		yield (xz[0], y, xz[1])

def fq_heights(query_cuboid):
	"""
	Parameter query_cuboid is a Cuboid representing the area you want to
	get heights for. The y component is ignored.
	
	The function returns a dictionary mapping (x, z) to (height).
	"""
	region = Cuboid(query_cuboid.x_range, (0,1), query_cuboid.z_range)
	result = {}

	for pos, h in query_blocks(
			region.generate_xz(),
			"world.getHeight(%d,%d)",
			int):
		result[pos] = h
	
	return result

def fq_heights_and_surface_ids(query_cuboid):
	"""
	Parameter query_cuboid is a Cuboid representing the area you want to
	get heights for. The y component is ignored.
	
	The function returns a dictionary mapping (x, z) to (height, block_id)
	where the block_id is the block at the surface.
	"""
	print('fq_heights_and_surface_ids')
	print('\tfq_heights')
	heightmap = fq_heights(query_cuboid)
	print('\t_heightmap_to_surface')
	surface_coords = to_xyz(heightmap)
	
	result = {}
	print('\tquery_blocks')
	for pos, blk in query_blocks(
			surface_coords,
			"world.getBlockWithData(%d,%d,%d)",
			parse_to_block):
		result[(pos[0], pos[2])] = (pos[1], blk)

	return result

def fq_heights_and_surface_id_filtered(cuboid: Cuboid):
	"""Returns a dict of (x, z): (height, Block) for the given cuboid, only taking into consideration "Ground Blocks"

	Args:
		cuboid
	Returns:
		dict of (x, z): (height, block_id)
	Example:
		>>> fq_heights_and_surface_id_filtered(Cuboid((-20, 20), (0, 1), (-20, 20)))
			returned heightmap of the area from -20 to 20 in the x direction and -20 to 20 in the z direction
	"""
	
	def yield_list_coords(d: dict):
		"""Yields the coordinates of a dict and the values RANGE_DOWN from coordinates"""
		RANGE_DOWN = 50
		for coord in d:
			x, z = coord[0], coord[1]
			y = d[x, z][0]
			# find information RANGE_DOWN down from the surface
			for i in range(RANGE_DOWN):
				yield x, y - i, z

	unfiltered_map = fq_heights_and_surface_ids(cuboid)

	ground_blocks = {STONE.id, GRASS.id, DIRT.id, COBBLESTONE.id, WATER_FLOWING.id, WATER_STATIONARY.id, 
					 LAVA_FLOWING.id, LAVA_STATIONARY.id, SAND.id, GRAVEL.id, IRON_ORE.id, COAL_ORE.id, SANDSTONE.id, MOSS_STONE.id, OBSIDIAN.id, FARMLAND.id, SNOW.id, ICE.id, SNOW_BLOCK.id, CLAY.id, TERRACOTTA_RED.id, GRASS_PATH.id, NETHERRACK.id}
	filtered_dictionary = {k: v for k, v in unfiltered_map.items() if v[1].id in ground_blocks}
	incorrect_dictionary = {k: v for k, v in unfiltered_map.items() if v[1].id not in ground_blocks}

	result = {}
	for pos, blk in query_blocks(
				yield_list_coords(incorrect_dictionary),
				"world.getBlockWithData(%d,%d,%d)",
				parse_to_block):
		x, y, z = pos
		if blk.id in ground_blocks:
			if (x, z) not in result:
				result[x, z] = (y, blk)
			elif result[x, z][0] < y or result[x, z][1].id not in ground_blocks:
				result[x, z] = (y, blk)
		elif (x, z) not in result:
			result[x, z] = (y, blk)

	for coord in result:
		filtered_dictionary[coord] = result[coord]
	return filtered_dictionary
