from enum import Enum
import random
import socket
from mcpi import minecraft
# from mcpi.block import Block
from block import *
from utils import *
from patterns import *
import time

SCAN_DISTANCE = 50
PATTERN_FILE = 'patterns.py'

class Facing(Enum):
	DOWN    = 1,
	UP      = 2,
	NORTH   = 3,
	SOUTH   = 4,
	WEST    = 5,
	EAST    = 6

class Brush():
	"""
	A Brush is created with a Pattern of blocks, and can be used to paint that
	pattern along a path.
	"""
	# These matrices describe how the pattern (dimensions u, v, w) should be
	# mapped on to the world (dimensions x, y, z)
	#
	# The rows of the matrix represent pattern space u, v, w and the columns
	# represent world space x, y, z.
	#
	# So, the matrix:      x  y  z
	#					u  1  0  0
	#					v  0  1  0
	#					w  0  0  1
	# indicates that the blocks in the pattern's u-axis should be mapped from
	# left to right along the world's x-axis. Similary, the v-axis is mapped
	# to the y axis and w to z.
	# 
	# This corresponds to the pattern image being drawn as though it was onto a
	# south facing wall, with any depth information (w-axis) protuding out of
	# the wall towards of the south.
	#
	# A mapping of -1 indicates the pattern should be drawn from right to left
	# along that axis. This means the matrix:      x  y  z
	#											u  0 -1  0
	#											v  1  0  0
	#											w  0  0  1
	# would be drawn the same as the example above, on the south wall, facing
	# south... but rotated 90 clockwise.
	#
	# I have worked out some of the logic for transforming a base matrix (say,
	# the first example above) into all possible facings/rotations/mirror/etc
	# but I don't quite understand the rotation of one matrix into a 90 without
	# breaking it into separate cases for South and East facing, versus North
	# and West, and Top/Bottom.  I am going to move on and just hard code them in
	# a dictionary.
	#
	# These base matrices below represent the rotations of a pattern a facing in
	# the specified direction. The first matrix for each facing is the pattern
	# drawn left to right, bottom to top and back to front (except for the top
	# and bottom matrices, for which the first matrices represent the pattern
	# oriented with the top facing north in the world). The subsequent 3
	# patterns are clock-wise rotations... 90, 180 and 270 degrees.
	#
	# Flipping, mirroring and inverting depth are quite simple - change the sign
	# in the relevant matrix row... e.g. flip the values in  matrix[1][*] to
	# flip the image, or in matrix[2][*] to invert the depth (same effect as
	# changing the facing and mirroring).

	base_matrices = { Facing.DOWN: 	[[[ -1,  0,  0],
									  [  0,  0, -1],
									  [  0, -1,  0]
									 ],
									 [[  0,  0,  1],
									  [ -1,  0,  0],
									  [  0, -1,  0]
									 ],
									 [[  1,  0,  0],
					   				  [  0,  0,  1],
					   				  [  0, -1,  0]
									 ],
									 [[  0,  0, -1],
									  [  1,  0,  0],
									  [  0, -1,  0]
									 ]],

					  Facing.UP: 	[[[  1,  0,  0],
									  [  0,  0,  1],
									  [  0,  1,  0]
									 ],
									 [[  0,  0,  1],
									  [  1,  0,  0],
									  [  0,  1,  0]
									 ],
									 [[ -1,  0,  0],
					   				  [  0,  0, -1],
					   				  [  0,  1,  0]
									 ],
									 [[  0,  0, -1],
									  [ -1,  0,  0],
									  [  0,  1,  0]
									 ]],

					  Facing.NORTH: [[[ -1,  0,  0],
									  [  0,  1,  0],
									  [  0,  0, -1]
									 ],
									 [[  0, -1,  0],
									  [ -1,  0,  0],
									  [  0,  0, -1]
									 ],
									 [[  1,  0,  0],
					   				  [  0, -1,  0],
					   				  [  0,  0, -1]
									 ],
									 [[  0,  1,  0],
									  [  1,  0,  0],
									  [  0,  0, -1]
									 ]],

					  Facing.SOUTH: [[[  1,  0,  0],
									  [  0,  1,  0],
									  [  0,  0,  1]
									 ],
									 [[  0, -1,  0],
									  [  1,  0,  0],
									  [  0,  0,  1]
									 ],
									 [[ -1,  0,  0],
					   				  [  0, -1,  0],
					   				  [  0,  0,  1]
									 ],
									 [[  0,  1,  0],
									  [ -1,  0,  0],
									  [  0,  0,  1]
									 ]],

					  Facing.WEST: 	[[[  0,  0,  1],
									  [  0,  1,  0],
									  [ -1,  0,  0]
									 ],
									 [[  0, -1,  0],
									  [  0,  0,  1],
									  [ -1,  0,  0]
									 ],
									 [[  0,  0, -1],
					   				  [  0, -1,  0],
					   				  [ -1,  0,  0]
									 ],
									 [[  0,  1,  0],
									  [  0,  0, -1],
									  [ -1,  0,  0]
									 ]],

					  Facing.EAST: 	[[[  0,  0, -1],
									  [  0,  1,  0],
									  [  1,  0,  0]
									 ],
									 [[  0, -1,  0],
									  [  0,  0, -1],
									  [  1,  0,  0]
									 ],
									 [[  0,  0,  1],
					   				  [  0, -1,  0],
					   				  [  1,  0,  0]
									 ],
									 [[  0,  1,  0],
									  [  0,  0,  1],
									  [  1,  0,  0]
									 ]]
					}

	def __init__(self, mc: minecraft.Minecraft, pattern: list, auto_reset: bool = True):
		self.mc = mc
		self.pattern = pattern
		self.auto_reset = auto_reset
		self.matrix = [[  1,  0,  0],
					   [  0,  1,  0],
					   [  0,  0,  1]]
		self.facing = Facing.UP
		self.rotation = 0
		self.flipped = False
		self.mirrored = False
		self.inverted = False
		# self.row = 0
		# self.col = 0

	def __str__(self) -> str:
		return self.name
	
	def __repr__(self) -> str:
		return self.__str__()

	def _select_matrix(self):
		self.matrix = Brush.base_matrices[self.facing][0]#[(self.rotation % 360) // 90]		# disabled rotation for the time being
		if self.mirrored:
			self.matrix[0][0] *= -1
			self.matrix[0][1] *= -1
			self.matrix[0][2] *= -1
		if self.flipped:
			self.matrix[1][0] *= -1
			self.matrix[1][1] *= -1
			self.matrix[1][2] *= -1
		if self.inverted:
			self.matrix[2][0] *= -1
			self.matrix[2][1] *= -1
			self.matrix[2][2] *= -1

	def print_matrix(self):
		print(f'    x   y   z')
		print(f'u{self.matrix[0][0]:>4}{self.matrix[0][1]:>4}{self.matrix[0][2]:>4}')
		print(f'v{self.matrix[1][0]:>4}{self.matrix[1][1]:>4}{self.matrix[1][2]:>4}')
		print(f'w{self.matrix[2][0]:>4}{self.matrix[2][1]:>4}{self.matrix[2][2]:>4}')
		print()

	def reset(self):
		self.facing = Facing.SOUTH
		self.rotation = 0
		self.mirrored = 0
		self.flipped = 0
		self.inverted = 0
		self._select_matrix()

	def set_pattern(self, pattern : 'Pattern'):
		self.pattern = pattern

	def orient(self, facing : Facing = Facing.UP, rotation : int = 0, mirrored : bool = False, flipped : bool = False, inverted : bool = False):
		"""
		Set all parameters of the brush. Rotation is specified in degrees (0, 90, 180, 270).
		"""
		self.facing = facing
		self.rotation = rotation
		self.mirrored = mirrored
		self.flipped = flipped
		self.inverted = inverted
		self._select_matrix()

	def face(self, facing : Facing):
		self.facing = facing
		self._select_matrix()

	def set_rotation(self, rotation=90):
		self.rotation = rotation
		self._select_matrix()

	def mirror(self):
		self.mirrored = not(self.mirrored)
		self._select_matrix()

	def flip(self):
		self.flipped = not(self.flipped)
		self._select_matrix()

	def invert(self):
		self.inverted = not(self.inverted)
		self._select_matrix()

	def draw_filled_rect(mc : minecraft.Minecraft, ll : Vector3, ur : Vector3, block : Block):
		mc.setBlocks(ll.x, ll.y, ll.z, ur.x, ur.y, ur.z, block)

	def draw_rect(mc : minecraft.Minecraft, ll : Vector3, ur : Vector3, block : Block):
		mc.setBlocks(ll.x, ll.y, ll.z, ur.x, ll.y, ll.z, block)
		mc.setBlocks(ll.x, ll.y, ll.z, ll.x, ll.y, ur.z, block)
		mc.setBlocks(ll.x, ll.y, ur.z, ur.x, ll.y, ur.z, block)
		mc.setBlocks(ur.x, ll.y, ll.z, ur.x, ll.y, ur.z, block)

	def draw(self, ax, ay, az, bx, by, bz, auto_reset=None):
		"""
		Draw the pattern along a baseline from a to b.
		Facing indicates the direction the pattern should be oriented:
			up, down, north, south, east, west
		"""

		ax, bx = min(ax, bx), max(ax, bx)
		ay, by = min(ay, by), max(ay, by)
		az, bz = min(az, bz), max(az, bz)

		x_step = self.matrix[0][0] + self.matrix[1][0] + self.matrix[2][0]

		if x_step > 0:
			x0 = ax
			x1 = bx
		else:
			x0 = bx
			x1 = ax

		y_step = self.matrix[0][1] + self.matrix[1][1] + self.matrix[2][1]

		if y_step > 0:
			y0 = ay
			y1 = by
		else:
			y0 = by
			y1 = ay

		z_step = self.matrix[0][2] + self.matrix[1][2] + self.matrix[2][2]

		if z_step > 0:
			z0 = az
			z1 = bz
		else:
			z0 = bz
			z1 = az

		bnum = 0
		for x in range(x0, x1 + x_step, x_step):
			for y in range(y0, y1 + y_step, y_step):
				for z in range(z0, z1 + z_step, z_step):
					blk = self.pattern.next()
					row = 0
					while blk is not None:
						
						# set column position
						x_offset = self.matrix[1][0] * row
						y_offset = self.matrix[1][1] * row
						z_offset = self.matrix[1][2] * row
						aisle = 0
						while blk is not None:
							# set aisle position
							# mc.postToChat(f'printing block {bnum}')
							bnum += 1
							self.mc.setBlock(x + x_offset + self.matrix[2][0] * aisle,
											 y + y_offset + self.matrix[2][1] * aisle,
											 z + z_offset + self.matrix[2][2] * aisle,
											 blk)
							aisle += 1
							blk = self.pattern.next()
						row += 1
						blk = self.pattern.next()
						# print('finishing w')
					# print('finishing v')
				# print('finishing u')
				
		# reset the brush after each draw, if the brush was set up that way, or passed as the draw param.
		if auto_reset or auto_reset is None and self.auto_reset:
			self.pattern.reset()

class Pattern:

	def write_to_file(pattern):
		with open(PATTERN_FILE,'a') as f:
			f.write(f'PATTERN-{time.time()} = {pattern}\n\n')
			print('Pattern written.')

	def convert_scan_to_pattern(mc : minecraft.Minecraft, corner_lsw : Vector3, corner_une : Vector3):
		pattern_list = []
		for u in range(corner_lsw.x + 1, corner_une.x):
			u_list = []
			for v in range(corner_lsw.y + 1, corner_une.y):
				v_list = []
				for w in range(corner_une.z + 1, corner_lsw.z, 1): # note z dir is reversed
					b = mc.getBlockWithData(u, v, w)
					v_list.append(b)
					# print(f'{x},{y},{z}: {b}')
				u_list.append(v_list)
			pattern_list.append(u_list)
		return pattern_list

	def scan(mc : minecraft.Minecraft):
		"""
		Looks for a volume of blocks demarcated with MARKER_BLOCKs placed in the
		lower SW corner, lower SE, lower NE and upper NE.

		The cubic volume defined by those blocks is printed in a format that can
		be used as a pattern.

		The pattern will use the EAST-WEST axis (starting from SOUTH end) as the
		brush path - that is, items on the NORTH and SOUTH in the world, will wind
		up on either side of the brush stroke path.
		"""
		MARKER_BLOCK = MAGENTA_WOOL

		# find SW corner
		pos_sw = mc.player.getTilePos()
		pos_sw.y -= 1
		m = mc.getBlockWithData(pos_sw.x, pos_sw.y, pos_sw.z)
		if m == MARKER_BLOCK:
			mc.postToChat(f'Found SW corner marker: {pos_sw.x}, {pos_sw.y}, {pos_sw.z}')
			x = 1
			# find SE corner
			marker_SE = mc.getBlockWithData(pos_sw.x + x, pos_sw.y, pos_sw.z)
			while marker_SE != MARKER_BLOCK and x < SCAN_DISTANCE:
				x += 1
				marker_SE = mc.getBlockWithData(pos_sw.x + x, pos_sw.y, pos_sw.z)
			if marker_SE == MARKER_BLOCK:
				pos_se = Vector3(pos_sw.x + x, pos_sw.y, pos_sw.z)
				mc.postToChat(f'Found SE corner marker: {pos_se.x}, {pos_se.y}, {pos_se.z}')
				z = 1
				# find NE corner
				marker_NE = mc.getBlockWithData(pos_se.x, pos_se.y, pos_se.z - z)
				while marker_NE != MARKER_BLOCK and z < SCAN_DISTANCE:
					z += 1
					marker_NE = mc.getBlockWithData(pos_se.x, pos_se.y, pos_se.z - z)
				if marker_NE == MARKER_BLOCK:
					pos_ne = Vector3(pos_se.x, pos_se.y, pos_se.z - z)
					mc.postToChat(f'Found NE corner marker: {pos_ne.x}, {pos_ne.y}, {pos_ne.z}')
					y = 1
					# find NE corner
					marker_ZNE = mc.getBlockWithData(pos_ne.x, pos_ne.y + y, pos_ne.z)
					while marker_ZNE != MARKER_BLOCK and y < SCAN_DISTANCE:
						y += 1
						marker_ZNE = mc.getBlockWithData(pos_ne.x, pos_ne.y + y, pos_ne.z)
					if marker_ZNE == MARKER_BLOCK:
						pos_zne = Vector3(pos_ne.x, pos_ne.y + y, pos_ne.z)
						mc.postToChat(f'Found upper NE corner marker: {pos_zne.x}, {pos_zne.y}, {pos_zne.z}')
						mc.postToChat('Writing pattern to file.')
						p = Pattern.convert_scan_to_pattern(mc, pos_sw, pos_zne)
						Pattern.write_to_file(p)
						# debug - switch the markers to gold when found
						# mc.setBlock(pos_sw.x, pos_sw.y, pos_sw.z, block.GOLD_BLOCK)
						# mc.setBlock(pos_se.x, pos_se.y, pos_se.z, block.GOLD_BLOCK)
						# mc.setBlock(pos_ne.x, pos_ne.y, pos_ne.z, block.GOLD_BLOCK)
						# mc.setBlock(pos_zne.x, pos_zne.y, pos_zne.z, block.GOLD_BLOCK)
					else:
						mc.postToChat('Could not find upper NE corner marker.')
				else:
					mc.postToChat('Could not find lower NE corner marker.')
			else:
				mc.postToChat('Could not find SE corner marker.')
		else:
			mc.postToChat('Could not find SW corner marker.')


	def __init__(self, block_list : list):
		self.pattern = block_list
		self.col = 0
		self.row = 0
		self.aisle = 0

	def reset(self):
		self.col = 0
		self.row = 0
		self.aisle = 0

	def next(self):
		if self.col >= len(self.pattern):
			self.col = 0
			self.row = 0
			self.aisle = 0
			#
			block = self.pattern[self.col][self.row][self.aisle]
			self.aisle += 1
			return block
			#
			# return None
		elif self.row >= len(self.pattern[self.col]):
			self.row = 0
			self.aisle = 0
			self.col += 1
			return None	
		elif self.aisle < len(self.pattern[self.col][self.row]):
			block = self.pattern[self.col][self.row][self.aisle]
			self.aisle += 1
			return block
		else:
			self.aisle = 0
			self.row += 1
			return None

if __name__ == "__main__":
	try:
		mc = minecraft.Minecraft.create()
	except socket.error as e:
		print("Cannot connect to Minecraft server")
		raise e

	pp = mc.player.getTilePos()
	
	if False:
		Pattern.scan(mc)
	if True:
		path_brush = Brush(mc, Pattern(TOWER))
		# b.print_matrix()
		path_brush.face(Facing.EAST)
		# b.print_matrix()
		# b.mirror()
		# b.print_matrix()
		path_brush.draw(pp.x, pp.y + 1, pp.z, pp.x + 100, pp.y, pp.z + 100)
