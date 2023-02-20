import random
import socket
from sqlite3 import Row
from utils import Vector3
from mcpi import minecraft


class Block:
    """
	Minecraft PI block description. Can be sent to Minecraft.setBlock/s
	"""

    def __init__(self, id, data=0):
        self.id = id
        self.data = data

    def __cmp__(self, rhs):
        return hash(self) - hash(rhs)

    def __eq__(self, rhs):
        return self.id == rhs.id and self.data == rhs.data

    def __hash__(self):
        return (self.id << 8) + self.data

    def withData(self, data):
        return Block(self.id, data)

    def __iter__(self):
        """Allows a Block to be sent whenever id [and data] is needed"""
        return iter((self.id, self.data))

    def __repr__(self):
        return "Block(%d, %d)" % (self.id, self.data)


AIR = Block(0)
STONE = Block(1)
GRANITE = Block(1, 1)
POLISHED_GRANITE = Block(1, 2)
DIORITE = Block(1, 3)
POLISHED_DIORITE = Block(1, 4)
ANDESITE = Block(1, 5)
POLISHED_ANDESITE = Block(1, 6)
GRASS = Block(2)
DIRT = Block(3)
COARSE_DIRT = Block(3, 1)
PODZOL = Block(3, 2)
COBBLESTONE = Block(4)
WOOD_PLANKS_OAK = Block(5)
WOOD_PLANKS = WOOD_PLANKS_OAK
WOOD_PLANKS_SPRUCE = Block(5, 1)
WOOD_PLANKS_BIRCH = Block(5, 2)
WOOD_PLANKS_JUNGLE = Block(5, 3)
WOOD_PLANKS_ACACIA = Block(5, 4)
WOOD_PLANKS_DARKOAK = Block(5, 5)
# saplings
SAPLING_OAK = Block(6)
SAPLING = SAPLING_OAK
SAPLING_SPRUCE = Block(6, 1)
SAPLING_BIRCH = Block(6, 2)
SAPLING_JUNGLE = Block(6, 3)
SAPLING_ACACIA = Block(6, 4)
SAPLING_DARKOAK = Block(6, 5)
BEDROCK = Block(7)
WATER_FLOWING = Block(8)
WATER = WATER_FLOWING
WATER_STATIONARY = Block(9)
LAVA_FLOWING = Block(10)
LAVA = LAVA_FLOWING
LAVA_STATIONARY = Block(11)
SAND = Block(12)
RED_SAND = Block(12, 1)
GRAVEL = Block(13)
GOLD_ORE = Block(14)
IRON_ORE = Block(15)
COAL_ORE = Block(16)
# tree trunks/vertical logs
WOOD_OAK_LOG_Y = Block(17)
WOOD = WOOD_OAK_LOG_Y
WOOD_SPRUCE_LOG_Y = Block(17, 1)
WOOD_BIRCH_LOG_Y = Block(17, 2)
WOOD_JUNGLE_LOG_Y = Block(17, 3)
# logs aligned to x axis
WOOD_OAK_LOG_X = Block(17, 4)
WOOD_SPRUCE_LOG_X = Block(17, 5)
WOOD_BIRCH_LOG_X = Block(17, 6)
WOOD_JUNGLE_LOG_X = Block(17, 7)
# logs aligned to z axis
WOOD_OAK_LOG_Z = Block(17, 8)
WOOD_SPRUCE_LOG_Z = Block(17, 9)
WOOD_BIRCH_LOG_Z = Block(17, 10)
WOOD_JUNGLE_LOG_Z = Block(17, 11)
# logs with no exposed surface
WOOD_OAK_LOG = Block(17, 12)
WOOD_SPRUCE_LOG = Block(17, 13)
WOOD_BIRCH_LOG = Block(17, 14)
WOOD_JUNGLE_LOG = Block(17, 15)
LEAVES_OAK = Block(18)
LEAVES = LEAVES_OAK
LEAVES_SPRUCE = Block(18, 1)
LEAVES_BIRCH = Block(18, 2)
LEAVES_JUNGLE = Block(18, 3)
SPONGE_DRY = Block(19)
SPONGE_WET = Block(18, 1)
GLASS = Block(20)
LAPIS_LAZULI_ORE = Block(21)
LAPIS_LAZULI_BLOCK = Block(22)
DISPENSER_DOWN = Block(23)
DISPENSER_UP = Block(23, 1)
DISPENSER_NORTH = Block(23, 2)
DISPENSER_SOUTH = Block(23, 3)
DISPENSER_WEST = Block(23, 4)
DISPENSER_EAST = Block(23, 5)
SANDSTONE = Block(24)
SANDSTONE_CHISELED = Block(24, 1)
SANDSTONE_CUT = Block(24, 2)
SANDSTONE = Block(24)
NOTE_BLOCK = Block(25)
# flowers
FLOWER_DANDELION = Block(37)
FLOWER_YELLOW = FLOWER_DANDELION
FLOWER_POPPY = Block(38)
FLOWER_CYAN = FLOWER_POPPY
FLOWER_BLUE_ORCHID = Block(38, 1)
FLOWER_ALLIUM = Block(38, 2)
FLOWER_AZURE_BLUET = Block(38, 3)
FLOWER_RED_TULIP = Block(38, 4)
FLOWER_ORANGE_TULIP = Block(38, 5)
FLOWER_WHITE_TULIP = Block(38, 6)
FLOWER_PINK_TULIP = Block(38, 7)
FLOWER_OXEYE_DAISY = Block(38, 8)
MUSHROOM_BROWN = Block(39)
MUSHROOM_RED = Block(40)
FLOWER_SUNFLOWER = Block(175)
FLOWER_LILAC = Block(175, 1)
FLOWER_TALL_GRASS = Block(175, 2)
FLOWER_LARGE_FERN = Block(175, 3)
FLOWER_ROSE_BUSH = Block(175, 4)
FLOWER_PEONY = Block(175, 5)
FLOWERPOT = Block(140)

# TODO complete block list!
BED_FOOT_SOUTH = Block(26, 2)
BED = BED_FOOT_SOUTH
BED_FOOT_NORTH = Block(26, 0)
BED_FOOT_EAST = Block(26, 1)
BED_FOOT_WEST = Block(26, 3)
BED_HEAD_SOUTH = Block(26, 10)
BED_HEAD_NORTH = Block(26, 8)
BED_HEAD_EAST = Block(26, 9)
BED_HEAD_WEST = Block(26, 11)

RAIL_POWERED = Block(27)
RAIL_DETECTOR = Block(28)
COBWEB = Block(30)
GRASS_TALL = Block(31)
DEAD_BUSH = Block(32)
WOOL = Block(35)
MAGENTA_WOOL = Block(35, 2)

GOLD_BLOCK = Block(41)
IRON_BLOCK = Block(42)
STONE_SLAB_DOUBLE = Block(43)
STONE_SLAB = Block(44)
BRICK_BLOCK = Block(45)
TNT = Block(46)
BOOKSHELF = Block(47)
MOSS_STONE = Block(48)
OBSIDIAN = Block(49)
TORCH = Block(50)
TORCH_UP = Block(50, 5)
FIRE = Block(51)

STAIRS_WOOD_UP_WEST = Block(53, 0)
STAIRS_WOOD_UP_EAST = Block(53, 1)
STAIRS_WOOD_UP_NORTH = Block(53, 2)
STAIRS_WOOD_UP_SOUTH = Block(53, 3)

STAIRS_WOOD_SPRUCE_UP_WEST = Block(134, 0)
STAIRS_WOOD_SPRUCE_UP_EAST = Block(134, 1)
STAIRS_WOOD_SPRUCE_UP_NORTH = Block(134, 2)
STAIRS_WOOD_SPRUCE_UP_SOUTH = Block(134, 3)

STAIRS_WOOD_BIRCH_UP_WEST = Block(135, 0)
STAIRS_WOOD_BIRCH_UP_EAST = Block(135, 1)
STAIRS_WOOD_BIRCH_UP_NORTH = Block(135, 2)
STAIRS_WOOD_BIRCH_UP_SOUTH = Block(135, 3)

STAIRS_WOOD_JUNGLE_UP_WEST = Block(136, 0)
STAIRS_WOOD_JUNGLE_UP_EAST = Block(136, 1)
STAIRS_WOOD_JUNGLE_UP_NORTH = Block(136, 2)
STAIRS_WOOD_JUNGLE_UP_SOUTH = Block(136, 3)

STAIRS_WOOD_ACACIA_UP_WEST = Block(163, 0)
STAIRS_WOOD_ACACIA_UP_EAST = Block(163, 1)
STAIRS_WOOD_ACACIA_UP_NORTH = Block(163, 2)
STAIRS_WOOD_ACACIA_UP_SOUTH = Block(163, 3)

STAIRS_WOOD_DARKOAK_UP_WEST = Block(164, 0)
STAIRS_WOOD_DARKOAK_UP_EAST = Block(164, 1)
STAIRS_WOOD_DARKOAK_UP_NORTH = Block(164, 2)
STAIRS_WOOD_DARKOAK_UP_SOUTH = Block(164, 3)

CHEST_NORTH = Block(54, 2)
CHEST_SOUTH = Block(54, 3)
CHEST_WEST = Block(54, 4)
CHEST_EAST = Block(54, 5)
DIAMOND_ORE = Block(56)
DIAMOND_BLOCK = Block(57)
CRAFTING_TABLE = Block(58)
FARMLAND = Block(60)
FURNACE_INACTIVE_EAST = Block(61, 5)
FURNACE_INACTIVE = FURNACE_INACTIVE_EAST
FURNACE_INACTIVE_NORTH = Block(61, 2)
FURNACE_INACTIVE_SOUTH = Block(61, 3)
FURNACE_INACTIVE_WEST = Block(61, 4)
FURNACE_ACTIVE = Block(62)
SIGN_STANDING = Block(63)
DOOR_WOOD = Block(64)
LADDER = Block(65)
RAIL = Block(66)

STAIRS_COBBLESTONE_UP_EAST = Block(67, 0)
STAIRS_COBBLESTONE = STAIRS_COBBLESTONE_UP_EAST
STAIRS_COBBLESTONE_UP_WEST = Block(67, 1)
STAIRS_COBBLESTONE_UP_SOUTH = Block(67, 2)
STAIRS_COBBLESTONE_UP_NORTH = Block(67, 3)
STAIRS_COBBLESTONE_UP_EAST_FLIP = Block(67, 4)
STAIRS_COBBLESTONE_UP_WEST_FLIP = Block(67, 5)
STAIRS_COBBLESTONE_UP_SOUTH_FLIP = Block(67, 6)
STAIRS_COBBLESTONE_UP_NORTH_FLIP = Block(67, 7)

SIGN_WALL = Block(68)
DOOR_IRON = Block(71)
REDSTONE_ORE = Block(73)
TORCH_REDSTONE = Block(76)
SNOW = Block(78)
ICE = Block(79)
SNOW_BLOCK = Block(80)
CACTUS = Block(81)
CLAY = Block(82)
SUGAR_CANE = Block(83)
JUKEBOX = Block(84)
FENCE = Block(85)
PUMPKIN = Block(86)
NETHERRACK = Block(87)
SOUL_SAND = Block(88)
GLOWSTONE_BLOCK = Block(89)
LIT_PUMPKIN = Block(91)
STAINED_GLASS = Block(95)
BEDROCK_INVISIBLE = Block(95)
TRAPDOOR = Block(96)
TRAPDOOR_TOP_HALF = Block(96, 8)
STONE_BRICK = Block(98)
STONE_BRICK_MOSS = Block(98, 1)
STONE_BRICK_CRACK = Block(98, 2)
STONE_BRICK_CHISEL = Block(98, 3)
GLASS_PANE = Block(102)
MELON = Block(103)
FENCE_GATE = Block(107)
STAIRS_BRICK = Block(108)

STAIRS_STONE_BRICK_UP_EAST = Block(109, 0)
STAIRS_STONE_BRICK = STAIRS_STONE_BRICK_UP_EAST
STAIRS_STONE_BRICK_UP_WEST = Block(109, 1)
STAIRS_STONE_BRICK_UP_SOUTH = Block(109, 2)
STAIRS_STONE_BRICK_UP_NORTH = Block(109, 3)
STAIRS_STONE_BRICK_UP_EAST_FLIP = Block(109, 4)
STAIRS_STONE_BRICK_UP_WEST_FLIP = Block(109, 5)
STAIRS_STONE_BRICK_UP_SOUTH_FLIP = Block(109, 6)
STAIRS_STONE_BRICK_UP_NORTH_FLIP = Block(109, 7)

REDSTONE_BLOCK = Block(152)

MYCELIUM = Block(110)
NETHER_BRICK = Block(112)
FENCE_NETHER_BRICK = Block(113)
STAIRS_NETHER_BRICK = Block(114)
BREWING_STAND = Block(117)
END_STONE = Block(121)
WOODEN_SLAB = Block(126)
STAIRS_SANDSTONE = Block(128)
EMERALD_ORE = Block(129)
RAIL_ACTIVATOR = Block(157)
TERRACOTTA_RED = Block(159, 14)
LEAVES2 = Block(161)
WOOD_ACACIA_LOG_Y = Block(162)
TRAPDOOR_IRON = Block(167)

CARPET_WHITE = Block(171)
CARPET_GRAY = Block(171, 7)
CARPET_LIGHT_GRAY = Block(171, 8)
CARPET_BROWN = Block(171, 12)
CARPET_BLACK = Block(171, 15)

FENCE_SPRUCE = Block(188)
FENCE_BIRCH = Block(189)
FENCE_JUNGLE = Block(190)
FENCE_DARK_OAK = Block(191)
FENCE_ACACIA = Block(192)
DOOR_SPRUCE = Block(193)
DOOR_BIRCH = Block(194)
DOOR_JUNGLE = Block(195)
DOOR_ACACIA = Block(196)
DOOR_DARK_OAK = Block(197)
GRASS_PATH = Block(208)
# MAGENTA_GLAZED_TERRACOTTA = Block(237)
GLOWING_OBSIDIAN = Block(246)
NETHER_REACTOR_CORE = Block(247)
CUSTOM_PATH = Block(999, 0)
CUSTOM_BUILDING = Block(999, 1)
CUSTOM_LAWN = Block(999, 2)

'''
random_material(choice) takes a string (choice) as an input and returns an appropriate randomised material.
Structure choices are: column, roof, floor, wall or chimney'''


def random_material(choice):
    if choice == 'column':
        materials = [WOOD_OAK_LOG_Y,
                     WOOD_OAK_LOG_Y,
                     WOOD_SPRUCE_LOG_Y,
                     WOOD_JUNGLE_LOG_Y,
                     STONE_BRICK,
                     BRICK_BLOCK]
    elif choice == 'wall':
        materials = [COBBLESTONE,
                     STONE_BRICK,
                     BRICK_BLOCK,
                     GRANITE,
                     WOOD_OAK_LOG,
                     WOOD_SPRUCE_LOG,
                     WOOD_PLANKS_SPRUCE,
                     WOOD_PLANKS_BIRCH,
                     WOOD_PLANKS_JUNGLE,
                     WOOD_PLANKS_ACACIA,
                     WOOD_PLANKS_DARKOAK]
    elif choice == 'roof':
        materials = [BRICK_BLOCK,
                     STONE_BRICK,
                     CLAY,
                     WOOD_PLANKS,
                     WOOD_PLANKS_OAK,
                     WOOD_PLANKS_SPRUCE,
                     WOOD_PLANKS_DARKOAK]
    elif choice == 'floor':
        materials = [WOOD_PLANKS_SPRUCE,
                     WOOD_PLANKS_BIRCH,
                     WOOD_PLANKS_JUNGLE,
                     WOOD_PLANKS_ACACIA,
                     WOOD_PLANKS_DARKOAK]
    elif choice == 'chimney':
        materials = [BRICK_BLOCK,
                     STONE,
                     GRANITE,
                     COBBLESTONE]
    elif choice == 'fence':
        materials = [FENCE,
                     FENCE_BIRCH,
                     FENCE_JUNGLE,
                     FENCE_ACACIA,
                     FENCE_SPRUCE,
                     FENCE_DARK_OAK]
    else:
        raise Exception("Choose a structure type")
    material = random.choice(materials)
    return material


'''
random_building_materials() ensures no two building materials are the same
'''


def random_building_materials():
    materials = dict()
    index_set = set()
    i = 0
    structures = ['column', 'wall', 'roof', 'floor', 'chimney']
    while i < len(structures):
        new_material = random_material(structures[i])
        index_set.add(new_material)
        if len(index_set) == i + 1:
            materials[structures[i]] = new_material
            i += 1
    return materials


if __name__ == "__main__":
    # create minecraft connection
    try:
        mc = minecraft.Minecraft.create()
    except socket.error as e:
        print("Cannot connect to Minecraft server")
        raise e

    if True:
        # draw block sampler - careful, it's very long and will bulldoze a large area
        # ---------------------------------------------------------------------------
        origin_x = 496
        origin_y = 65
        origin_z = 566
        mc.setBlocks(origin_x + 1, origin_y - 1, origin_z + 1, origin_x - 500, origin_y + 25, origin_z - 16, 0)
        mc.setBlocks(origin_x + 1, origin_y - 1, origin_z + 1, origin_x - 500, origin_y - 1, origin_z - 16, 2)

        for i in range(0, 255):
            mc.setBlocks(origin_x - i * 2, origin_y, origin_z + 1, origin_x - i * 2, origin_y, origin_z - 16, 49)
            for d in range(0, 15):
                mc.setBlock(origin_x - i * 2 - 1, origin_y, origin_z - d, i, d)
