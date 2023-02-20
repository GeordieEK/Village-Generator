import socket
from random import randint

from mcpi import block, minecraft
from mcpi.minecraft import Vec3
import socket
from block import *
from utils import Vector3, Rectangle, Vector2


# TODO: Ideas: gardens, trees, streetlamps, fountains, wells, animal pens (see spawnEntity);
#  giving some houses fenced-off swimming pools; adding furniture inside the houses.

# TODO: This feels inefficient, there's some repeated code etc. Could we improve it by extending classes?
#  Or perhaps bundling it all into a decoration class with different methods for different structures

# TODO: Pick nicer blocks for structures

class Fountain:
    def __init__(self, mc, x, y, z):
        self.mc = mc
        self.x = x
        self.y = y
        self.z = z

        self.build()

    def build(self):
        # Fountain base level
        for x in range(self.x - 3, self.x + 4):
            for z in range(self.z - 3, self.z + 4):
                if z == self.z - 3 or z == self.z + 3 or x == self.x - 3 or x == self.x + 3:
                    self.mc.setBlock(x, self.mc.getHeight(x, z), z, 0)
                else:
                    self.mc.setBlock(x, self.mc.getHeight(x, z) + 1, z, 1)
        # Fountain upper level
        for x in range(self.x - 1, self.x + 2):
            for z in range(self.z - 1, self.z + 2):
                self.mc.setBlock(x, self.mc.getHeight(x, z) + 1, z, 1)
                if (x == self.x - 1 or x == self.x + 1) and (z == self.z - 1 or z == self.z + 1):
                    self.mc.setBlock(x, self.mc.getHeight(x, z) + 1, z, 1)
        self.mc.setBlock(self.x, self.mc.getHeight(x, z) + 2, self.z, 1)
        # Flowing Water
        self.mc.setBlock(self.x, self.mc.getHeight(x, z) + 1, self.z, 8)


class Garden:
    """
    Garden will build tilled land with assorted plants/crops in an area of whatever dimensions you pass in.
    Garden takes Vector 3 inputs in top_left and bottom_right configuration.
    """

    def __init__(self, mc, top_left, bottom_right):
        # Minecraft connection
        self.mc = mc
        # Coords
        self.top_left = top_left
        self.bottom_right = bottom_right
        # Run build method
        self.build()

    def build(self):
        # Unpack coords
        x1, y, z1 = Vec3(self.top_left.x, self.top_left.y, self.top_left.z)
        x2, _, z2 = Vec3(self.bottom_right.x, self.bottom_right.y, self.bottom_right.z)
        # List of crops
        crop_list = [FLOWER_DANDELION, FLOWER_POPPY, FLOWER_BLUE_ORCHID, FLOWER_ALLIUM, FLOWER_AZURE_BLUET, FLOWER_RED_TULIP, FLOWER_ORANGE_TULIP, FLOWER_WHITE_TULIP, FLOWER_PINK_TULIP, FLOWER_OXEYE_DAISY]
        for x in range(x1, x2):
            crop = random.choice(crop_list)
            if x % 2 == 0:
                for z in range(z1, z2):
                    if z == z1 or z == (z2 - 1) or z % 4 == 0: # put water at the ends to keep the farmland from turning to dirt
                        self.mc.setBlock(x, y, z, WATER_STATIONARY)
                        self.mc.setBlock(x, y + 1, z, TRAPDOOR)
                    else:
                        self.mc.setBlock(x, y, z, FARMLAND)
                        self.mc.setBlock(x, y + 1, z, crop)


class Well:
    def __init__(self, mc, centre_point):
        # Minecraft connection
        self.mc = mc
        # Centre of the well
        self.centre_point = centre_point
        # Run build method
        self.build()

    def build(self):
        # TODO: Random number of mossy stone
        stone_coords = ((1, 3), (2, 2), (2, 4), (3, 1), (5, 1))
        empty_coords = ((2, 3), (3, 3), (3, 4))
        # Unpack coords
        x, y, z = Vec3(self.centre_point.x, self.centre_point.y, self.centre_point.z)
        for y in enumerate(range(y, y - 5, -1)):
            print("y is ", y)
            for x_relative, x_absolute in enumerate(range(x, x + 5)):
                for z_relative, z_absolute in range(z, z + 5):
                    print(x, z)
                    if (x_relative, z_relative) in stone_coords or (z, x) in stone_coords:
                        print("stone", x, z)
                        self.mc.setBlock(x, z - 1, z, 1)
                    elif (x, z) in empty_coords or (z, x) in empty_coords:
                        self.mc.setBlock(x, z - 1, z, 0)
                        print("empty", x, z)


class Pool:
    def __init__(self, mc, point1: Vector2, point2: Vector2, height: int):
        # Minecraft connection
        self.mc = mc
        self.point1, self.point2 = point1, point2
        self.height = height
        self.rect = Rectangle(point1, point2)
        # Run build method
        self.build(self.rect, self.height)

    def build(self, rect: Rectangle, height: int):
        rect = rect.expanded_by(-1)
        self.mc.setBlocks(rect.small_corner.x, height - 1, rect.small_corner.z,
                          rect.large_corner.x, height - 1, rect.large_corner.z, block.WATER)
        rect = rect.expanded_by(1)
        fence = Fence(mc, rect, height)


class Fence:
    def __init__(self, mc, rect, height: int):
        # Minecraft connection
        self.mc = mc
        self.height = height
        self.rect = rect
        # Run build method
        self.build(self.rect, self.height)

    def build(self, rect: Rectangle, height: int):
        fence_choice = block.random_material('fence')
        corners = [(rect.x0, rect.z1), (rect.x1, rect.z1), (rect.x1, rect.z0), (rect.x0, rect.z0)]
        for side in range(-1, 3):
            self.mc.setBlocks(corners[side][0], height, corners[side][1],
                              corners[side + 1][0], height, corners[side + 1][1], fence_choice)
        self.mc.setBlock(corners[3][0], height, corners[3][1], block.AIR)
        self.mc.setBlock(corners[3][0], height, corners[3][1], fence_choice)
        # self.mc.setBlocks(corners[2][0], height, corners[2][1],
        #                   corners[3][0], height, corners[3][1], block.AIR)


if __name__ == "__main__":
    try:
        mc = minecraft.Minecraft.create()
    except socket.error as e:
        print("Cannot connect to Minecraft server")
        raise e
    player_pos = mc.player.getTilePos()
    other_pos = Vec3(player_pos.x + 30, player_pos.y, player_pos.z + 25)
    garden = Garden(mc, player_pos, other_pos)
