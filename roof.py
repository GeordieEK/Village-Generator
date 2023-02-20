"""
Functions to create roof, using (x1, z1), (x2, z2) and original height 

 To use create new instance of roof and provide bottom left and top right coords (x1,z1) BL and (x2, z2)TR.
 Also needs the height of the roof
"""

from mcpi.minecraft import Minecraft
import block
from mcpi.minecraft import Vec3
from random import randint
import math

mc = Minecraft.create()


class Roof:
    def __init__(self, x1, x2, z1, z2, y, wall_type=block.STONE, block_type=block.TERRACOTTA_RED) -> None:
        self.x1 = x1
        self.x2 = x2
        self.z1 = z1
        self.z2 = z2
        self.y = y
        self.block_type = block_type
        self.wall_type = wall_type
        self.build_roof()
        # If building is big enough, add chimney with random chance
        if randint(1, 2) == 1 and abs(x1 - x2) > 5 and abs(z1 - z2) > 5:
            self.chimney()

    # function that randomly decides which roof style to use
    def build_roof(self):
        val = randint(1, 2)
        # mc.postToChat(val)
        if val == 1:
            self.roof1(self.x1, self.x2, self.z1, self.z2, self.y)
        else:
            self.roof2(self.x1, self.x2, self.z1, self.z2, self.y)

    # function to build rectangular shells
    def build_rectangle(self, length, width, x, y, z):
        # build length-wise
        for i in range(length + 1):
            # set blocks parallel to each other
            mc.setBlock(x + i, y, z, self.block_type)
            mc.setBlock(x + i, y, z - width, self.block_type)
        # build width-wise
        for j in range(width + 1):
            mc.setBlock(x, y, z - j, self.block_type)
            mc.setBlock(x + length, y, z - j, self.block_type)

    # roof style 1 - square based pyramid like
    # recursive function to repeatedly make shells (creating roof)
    def roof1(self, x1, x2, z1, z2, y, roof_height=0):
        # 2 base cases: 
        if roof_height > 10:
            return
        # a square in which both length and width are 0 and the point needs to be added
        if int(math.fabs(x2 - x1)) == 1 or int(math.fabs(z2 - z1)) == 1:
            self.build_rectangle(int(math.fabs(x2 - x1)), int(math.fabs(z2 - z1)), x1, y, z1)
            return
        # the  rectangle in which it has already flattened out
        elif int(math.fabs(x2 - x1)) == 0 or int(math.fabs(z2 - z1)) == 0:
            self.build_rectangle(int(math.fabs(x2 - x1)), int(math.fabs(z2 - z1)), x1, y, z1)
            return
        else:
            self.build_rectangle(int(math.fabs(x2 - x1)), int(math.fabs(z2 - z1)), x1, y, z1)
            # create next shell, length and width decreased by 2 and height increased by 1
            self.roof1(x1 + 1, x2 - 1, z1 - 1, z2 + 1, y + 1, roof_height + 1)

    # helper function, builds walls for empty space
    def build_W(self, x1, x2, z1, z2, y):
        width = int(math.fabs(z2 - z1)) + 1  # +1 due to for loop not being inclusive of end val
        for i in range(width):
            mc.setBlock(x1, y, z1 - i, self.wall_type)
            mc.setBlock(x2, y, z1 - i, self.wall_type)

    # helper function, recursively builds walls until the space is completely filled
    def walls(self, x1, x2, z1, z2, y):
        # if int(math.fabs(z2 - z1)) == 1:
        #     self.build_W(z1, z2, y, x1, x2)
        #     return
        if int(math.fabs(z2 - z1)) <= 1:
            self.build_W(x1, x2, z1, z2, y)
            return
        else:
            self.build_W(x1, x2, z1, z2, y)
            self.walls(x1, x2, z1 - 1, z2 + 1, y + 1)
    
    # helper function to build roof parallel until the meet
    def build_parallel(self, x1, x2, z1, z2, y):
        x1 -= 1
        z1 += 1
        z2 -= 1
        y -= 1
        for i in range(abs(x2 - x1) + 2):
            mc.setBlock(x1 + i, y, z1, self.block_type)
            mc.setBlock(x1 + i, y, z2, self.block_type)
    # tent style roof
    def roof2(self, x1, x2, z1, z2, y, recursion_level=0):
        # build final two levels then stop
        if abs(z2 - z1) == 0:
            self.build_parallel(x1, x2, z1, z2, y)
            self.build_parallel(x1, x2, z1 - 1, z2 + 1, y + 1)
            return
        elif abs(z2 - z1) == 1:
            self.build_parallel(x1, x2, z1, z2, y)
            self.build_parallel(x1, x2, z1 - 1, z2 + 1, y + 1)
            return
        # keep going until the end
        else:
            self.build_parallel(x1, x2, z1, z2, y)
            self.roof2(x1, x2, z1 - 1, z2 + 1, y + 1, recursion_level + 1)
        if recursion_level == 0: # build side walls
            self.walls(x1, x2, z1 - 1, z2 + 1, y)

    def chimney(self):
        # Get center of building and then offset by randomised integer
        x_factor = abs(self.x1 - self.x2) // 2 + randint(0, 2)
        z_factor = abs(self.z1 - self.z2) // 2 + randint(0, 2)
        chimney_choice = block.random_material("chimney")
        x, y, z = self.x1 + 3, self.y, self.z1 - 3
        mc.setBlocks(x, y, z,
                     x + 1, y + 4, z + 1, chimney_choice)
