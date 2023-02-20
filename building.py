from random import randint
from typing import Any

from mcpi.minecraft import Minecraft
from mcpi.minecraft import Vec3

import block
from block import *
from furnish import Furnish
from roof import Roof
from utils import Rectangle, Vector2
from wall import Wall


class Building:

    def __init__(self, mc, plot, height):
        # Building Parameters
        self.number_of_floors = randint(1, 2)
        self.floor_height = randint(2, 3)
        self.min_dimension = randint(5, 7)
        self.min_ratio = round(random.uniform(0.25, 0.30), 2)
        self.door_placement = randint(-1, 2)  # Selects which wall will place a door, not where the door is
        #   -1 = west, 0 = south, 1 = east, 2 = north...
        self.door_type = -1  # Initialise Door_type to insert no wall

        # Randomise materials
        material_dict = block.random_building_materials()
        self.wall_choice = material_dict['wall']
        self.column_choice = material_dict['column']
        self.roof_choice = material_dict['roof']
        self.floor_choice = material_dict['floor']

        # Internal walls can't build over these
        self.safety_blocks = {AIR, GLASS, GLASS_PANE, DOOR_WOOD, DOOR_WOOD.withData(3), DOOR_WOOD.withData(11)}

        # Minecraft connection
        self.mc = mc
        # Door coordinates to be generated when door is placed
        self.door_coords = None
        self.x1, self.z2 = plot.small_corner
        self.x2, self.z1 = plot.large_corner
        self.footprint = plot
        self.base_height = height
        self.rooms = []
        self.build()

    def build(self):

        # clear space above building footprint
        self.mc.setBlocks(self.footprint.small_corner.x, self.base_height, self.footprint.small_corner.z,
                          self.footprint.large_corner.x, 255, self.footprint.large_corner.z, AIR)

        width = abs(self.x2 - self.x1)
        length = abs(self.z2 - self.z1)

        for floor_num in range(self.number_of_floors):
            self.rooms.append([{(self.x1, self.z1): (self.x2, self.z2)}])
            ceiling_adj = 0
            if floor_num == 1:  # If second storey, build second storey floor slightly higher
                # to account for ground-floor being dug in and floor narrower so it doesn't appear outside
                ceiling_adj = 2
                self.footprint = self.footprint.expanded_by(-1)
            # Build the floor
            self.build_floor(self.footprint,
                             self.base_height + (floor_num * self.floor_height + ceiling_adj),
                             block=self.floor_choice)

            # Wall coordinates
            corners = [(self.x1, self.z1), (self.x2, self.z1), (self.x2, self.z2), (self.x1, self.z2)]

            for side in range(-1, 3):
                # Door will only be placed on one side, chosen at random
                # Door will not be placed on second floor
                if side == self.door_placement and floor_num != 1:
                    self.door_type = 1
                wall = Wall(self.mc,
                            Vec3(corners[side][0], self.base_height, corners[side][1]),
                            Vec3(corners[side + 1][0], self.base_height, corners[side + 1][1]), self.floor_height + 1,
                            base_height=self.base_height + floor_num * self.floor_height + 1 + ceiling_adj,
                            door=self.door_type, wall_type=self.wall_choice)
                self.door_type = -1
                if wall.door_coords is not None:
                    self.door_coords = wall.door_coords[0]

            # Calculate top of building
            building_top = self.base_height + floor_num * self.floor_height + self.floor_height + ceiling_adj + 1
            # self.rooms = [(self.x1,self.z1,self.x2,self.z2)]
            # Add the internal rooms
            self.recursive_build(self.x1, self.x2, self.z1, self.z2,
                                 self.base_height + floor_num * self.floor_height + ceiling_adj + 1,
                                 self.footprint.width > self.footprint.height, floor_num)
        # Add the roof
        roof = Roof(self.x1, self.x2, self.z1, self.z2, building_top + 2,
                    block_type=self.roof_choice, wall_type=self.wall_choice)

        # Build the attic floor
        if self.number_of_floors == 1:
            # If building is only one storey, attic roof needs to be shrunk to stop conflict with roof
            self.footprint = self.footprint.expanded_by(-1)
        self.build_floor(self.footprint, building_top + 2, block=self.column_choice)
        # Place columns
        for side in range(-1, 3):
            self.mc.setBlocks(corners[side][0], self.base_height, corners[side][1],
                              corners[side][0], building_top + 1, corners[side][1], self.column_choice)
        f = Furnish(self.rooms, self.number_of_floors, self.base_height+1, self.floor_height, [self.x1,self.z1, self.x2, self.z2])

    def build_floor(self, floor_rect: Rectangle, height: int, block: Block = WOOD_PLANKS_OAK):
        self.mc.setBlocks(floor_rect.small_corner.x, height, floor_rect.small_corner.z,
                          floor_rect.large_corner.x, height, floor_rect.large_corner.z, block)

    # Recursive helper function to build rooms
    def recursive_build(self, x1, x2, z1, z2, floor_height, is_vertical_split, floor_num):
        width = abs(x2 - x1)
        length = abs(z2 - z1)
        # area = width * length
        # Base case of room size defined by minimum lengths and minimum area
        # Also includes a random chance to end recursion early for larger rooms and more variability
        # TODO: add back in random early end randint(1, 10) == 1 or
        if width < self.min_dimension or length < self.min_dimension \
                or width / length < self.min_ratio or length / width < self.min_ratio:
            return
        else:
            # Split vertical
            if is_vertical_split:
                # Split building along x-axis including some random chance
                split_points = list(range(self.min_dimension, width - self.min_dimension + 2))
                if not split_points:
                    return
                split = random.choice(split_points)
                # Move walls if they conflict with doors or windows
                while self.mc.getBlockWithData(Vec3(x1 + split, self.base_height + 2, z1)) in self.safety_blocks \
                        or self.mc.getBlockWithData(Vec3(x1 + split, self.base_height + 2, z1 - length)) in self.safety_blocks:
                    split_points.remove(split)
                    if not split_points:
                        return
                    split = random.choice(split_points)
                # Build split wall
                wall = Wall(self.mc,
                            Vec3(x1 + split, floor_height, z1),
                            Vec3(x1 + split, floor_height, z1 - length), self.floor_height + 1,
                            base_height=floor_height, windows=False, door=randint(0, 1), wall_type=self.wall_choice)
                # swap direct back to original
                self.splitter(self.rooms, split, (is_vertical_split), x1, x2, z1, z2, floor_num)
                self.recursive_build(x1, x1 + split, z1, z2, floor_height, not is_vertical_split, floor_num)
                self.recursive_build(x1 + split, x2, z1, z2, floor_height, not is_vertical_split, floor_num)
            # Split horizontal
            else:
                # Split building along z-axis
                split_points: list[Any] = list(range(self.min_dimension, length - self.min_dimension + 2))
                if not split_points:
                    return
                split = random.choice(split_points)
                # Move walls if they conflict with doors or windows
                while self.mc.getBlockWithData(Vec3(x1, self.base_height + 2, z1 - split)) in self.safety_blocks \
                        or self.mc.getBlockWithData(Vec3(x1 + width, self.base_height + 2, z1 - split)) in self.safety_blocks:
                    split_points.remove(split)
                    if not split_points:
                        return
                    split = random.choice(split_points)

                # Build split wall
                wall = Wall(self.mc,
                            Vec3(x1, floor_height, z1 - split),
                            Vec3(x1 + width, floor_height, z1 - split), self.floor_height + 1,
                            base_height=floor_height, windows=False, door=randint(0, 1), wall_type=self.wall_choice)
                # swap direct back to original
                self.splitter(self.rooms, split, is_vertical_split, x1, x2, z1, z2, floor_num)
                self.recursive_build(x1, x2, z1, z1 - split, floor_height, not is_vertical_split, floor_num)
                self.recursive_build(x1, x2, z1 - split, z2, floor_height, not is_vertical_split, floor_num)

    def get_door_coords(self):
        # x,y,z = , self.door_coords.y, self.door_coords.y
        if self.door_coords[0] == self.x1:
            if self.door_coords[2] == self.z1:
                return self.door_coords[0], self.door_coords[1], self.door_coords[2] - 1
            else:
                return self.door_coords[0] - 1, self.door_coords[1], self.door_coords[2]
        else:
            if self.door_coords[2] == self.z1:
                return self.door_coords[0], self.door_coords[1], self.door_coords[2] + 1
            else:
                return self.door_coords[0] + 1, self.door_coords[1], self.door_coords[2]

    # function to get room coordinates
    def splitter(self, rooms, split_dist, split_direction, x1, x2, z1, z2, floor_num):
        # loop through list of rooms
        for index, room in enumerate(rooms[floor_num]):
            # try except due to keyErrors
            try:
                # remove room that is being split
                if room[(x1, z1)] == (x2, z2):
                    rooms[floor_num].pop(index)
                    # del room[x1, z1]
            except:
                pass
            try:
                if room[(x2, z2)] == (x1, z1):
                    rooms[floor_num].pop(index)
                    # del room[x1, z1]
            except:
                pass
        # add two result rooms based on correct direction given
        if split_direction:
            room1 = {(x1, z1): (x1 + split_dist, z2)}
            room2 = {(x1 + split_dist, z1): (x2, z2)}
            rooms[floor_num].append(room1)
            rooms[floor_num].append(room2)
        else:
            room1 = {(x1, z1): (x2, z1 - split_dist)}
            room2 = {(x1, z1 - split_dist): (x2, z2)}
            rooms[floor_num].append(room1)
            rooms[floor_num].append(room2)

    def get_doormat(self):
        """
        Returns the block just outside the door - a tuple of Vector2s,
        the first representing the x, z co-ordinates and the second representing
        the direction away from the wall/building.
        """
        door_pos = Vector2(self.door_coords[0], self.door_coords[2])
        door_facing = Vector2(-1, 0)  # door_placement = -1, signifies west
        if self.door_placement == 0:
            door_facing = Vector2(0, 1)  # south
        elif self.door_placement == 1:
            door_facing = Vector2(1, 0)  # east
        elif self.door_placement == 2:
            door_facing = Vector2(0, -1)  # north
        return (door_pos + door_facing, door_facing)


# TEST CASE
if __name__ == "__main__":
    # create minecraft connection
    mc = Minecraft.create()

    player_pos = mc.player.getTilePos()
    v = Rectangle(Vector2(player_pos.x + 5, player_pos.z + 5), Vector2(player_pos.x + 19, player_pos.z + 15))
    # other_pos = Vec3(player_pos.x + 10, player_pos.y, player_pos.z + 15)

    testHouse = Building(mc, v, player_pos.y - 1)
    # testHouse.get_room_coords()
    # mc.setBlocks(player_pos.x,player_pos.y,player_pos.z,player_pos.x-50,player_pos.y+50,player_pos.z+50,0)
