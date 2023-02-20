from mcpi import minecraft
from utils import *
import random
import block

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from plot import Plot

CHANCE_OF_ANYTHING = 1/8.0
CHANCE_OF_GRASS = 2/3.0
CHANCE_OF_FLOWERS = 3/4.0
CHANCE_OF_MUSHROOMS = 1/2.0

FLOWERS = [     block.FLOWER_DANDELION,
				block.FLOWER_POPPY,
				block.FLOWER_BLUE_ORCHID,
				block.FLOWER_ALLIUM,
				block.FLOWER_AZURE_BLUET,
				block.FLOWER_RED_TULIP,
				block.FLOWER_ORANGE_TULIP,
				block.FLOWER_WHITE_TULIP,
				block.FLOWER_PINK_TULIP,
				block.FLOWER_OXEYE_DAISY,
				block.FLOWER_SUNFLOWER,
				block.FLOWER_LILAC,
				block.FLOWER_LARGE_FERN,
				block.FLOWER_ROSE_BUSH,
				block.FLOWER_PEONY]

MUSHROOMS = [   block.MUSHROOM_BROWN,
				block.MUSHROOM_RED]

GRASS =	[		block.FLOWER_TALL_GRASS]
				
SAPLINGS = [	block.SAPLING_OAK,
				block.SAPLING_SPRUCE,
				block.SAPLING_BIRCH,
				block.SAPLING_JUNGLE,
				block.SAPLING_ACACIA,
				block.SAPLING_DARKOAK]

class Yard:
	def __init__(self, mc: minecraft.Minecraft, plot: 'Plot', total_plot: Rectangle, building_plot: Rectangle, base_height: int):

		###	GARDENING TIME!
		mc.postToChat(f'Planting flowers and saplings.')
		for x in range(*total_plot.x_range()):
			for z in range(*total_plot.z_range()):
				if not building_plot.contains(Vector2(x, z)) and random.random() < CHANCE_OF_ANYTHING:
					plant = None
					if random.random() < CHANCE_OF_GRASS:
						plant = GRASS[random.randrange(0, len(GRASS))]
					elif random.random() < CHANCE_OF_FLOWERS:
						plant = FLOWERS[random.randrange(0, len(FLOWERS))]
					elif random.random() < CHANCE_OF_MUSHROOMS:
						plant = MUSHROOMS[random.randrange(0, len(MUSHROOMS))]
					else:
						plant = SAPLINGS[random.randrange(0, len(SAPLINGS))]
					mc.setBlock(x, plot.village.map.height(x,z) + 1, z, plant)