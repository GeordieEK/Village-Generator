from mcpi.minecraft import Minecraft
import block
from random import randint, randrange
from utils import Vector2

"""
STANDARD FOR ORIENTATION:(tl - topleft block)
#1 - tl facing east, #2 tl facing north, #3 tl facing west, #4, tl facing south

THE ADD__ FUNCTIONS:
- START: the x1,z1 block you wish to start at (should be closets to top left)
- END: a Vector2 object of how far you want the object to be in each direction
e.g if you want it to be 2 x 4 (2 wide x, 4 wide z) end = (2,4)
- HEIGHT/Y: the height of the floor 
- ORIENTATION: int value based on standard above
"""

mc = Minecraft.create()
class Furnish:
    def __init__(self, rooms, num_floors, floor_height, base_height, corners):
        # set the orienations 
        self.east = 1
        self.north = 2
        self.west = 3
        self.south = 4
        # set the corners of the house
        self.x1 = corners[0]
        self.z1 = corners[1]
        self.x2 = corners[2]
        self.z2 = corners[3]
        self.stairs_done = False
        self.boundary_zone = []
        self.num_floors = num_floors
        self.floor_on = 0
        self.floor_height = floor_height
        self.base_height = base_height
        self.all_doors = []
        self.stairs_start = None
        self.stairs_o = 0
        # door_location = Vector2(door_location[0].x - door_location[1].x, door_location[0].z - door_location[1].z)
        self.furnish_room(rooms,num_floors,floor_height,base_height+floor_height+2)
        
    # function to correctly orient end points for add_ functions
    def orientate_end(self, orientation, end):        
        if orientation == self.east:
            end = Vector2(end.x * -1, end.z * 1)     # east
        elif orientation == self.north:
            end = Vector2(end.x * -1, end.z * 1)    # north
        elif orientation == self.west:
            end = Vector2(end.x * 1, end.z * 1)     # west
        else:
            end = Vector2(end.x * -1, end.z * -1)      # south

        return end
    
    # choose opposite orientaiton e.g East(1)/West(3) goes to North(2)/South(4)
    def choose_orientation(self, orientation):
        if orientation == self.east or orientation == self.west: # if east or west randomly choose north or south
            return randrange(2,5,2)
        else:
            return randrange(1,4,2)


    """
    Starting points:
    |---------------|
    |X ->           | 
    |^             ^|
    ||             ||
    |X ->          X|
    |---------------|
    Bottom left corner is the top left of the room where up in the diagram in north in minecraft and right is east in minecraft
    """
    # helper function to intiate start coordinates diagonally across off the wall
    def orientate_start(self, x1, z1, x2, z2, orientation):
        if orientation == self.east:
            start = Vector2(x1+1,z1-1)     # east
        elif orientation == self.north:
            start = Vector2(x1+1,z1-1)    # north
        elif orientation == self.west:
            start = Vector2(x2-1,z1-1)     # west
        else:
            start = Vector2(x1+1,z2+1)      # south

        return start
    # main function that will loop through all rooms and floors and give them rooms
    def furnish_room(self, rooms, num_floors, floor_height, base_height):
        for i in range(num_floors):
            self.floor_on += i
            if i == 1:
                height = base_height
            else:
                height= floor_height
            for room in rooms[i]:
                    x1, x2, z1, z2, y = self.getCoords(room, height)
                    print(x1, z1, x2, z2, y)
                    length = abs(x2-x1)-1 # -1 due to walls
                    width = abs(z2-z1)-1 # -1 due to walls
                    area = length * width
                    stairs_room = 0
                    lastroom = -1
                    # check if there is enouh space to build stairs
                    if length > self.base_height+2 or width > self.base_height+2:
                        if (not self.stairs_done) and (num_floors != 1): # check the stairs haven't been built and there is 2 floors
                            if room is not rooms[0][lastroom]: # if the room isn't the last room in the list randomly decide
                                stairs_room = randint(0,1)
                            else:
                                stairs_room = 1 # create stairs if last room

                    if area == length or area == width or area == 4:
                        print("Room too small")
                    elif stairs_room == 1: # make stairs room
                        print("STAIRS")
                        self.stairs_done = True
                        self.create_stairs_room(x1,z1,x2,z2,y, base_height, length, width)
                    # validation for smaller rooms change stair type and create stairs
                    elif room is rooms[0][lastroom] and (length <= self.base_height+2 or width <= self.base_height+2) and not self.stairs_done and (num_floors != 1):
                    # self.base_height == 3 and (length == 4 or width == 4) and not self.stairs_done:
                        print("STAIRS")
                        self.stairs_done = True
                        self.create_stairs_room(x1,z1,x2,z2,y, base_height, length, width, gap=False)
                    else:
                        room_options, index, option = self.choose_room(length, width)
                        room_options[index][option](x1,z1,x2,z2,y, length, width)

            self.ensure_doorway_clear(self.all_doors, height, height+2)
            self.all_doors = []
        self.ensure_access_to_stairs()
        self.clear_above_stairs(floor_height+self.base_height+2, floor_height+self.base_height+5)
    
    # helper func to choose either living, dining or bedrooms
    def choose_room(self, length, width):        
        _room_options = ["living", "dining", "bed"]
        room_options = [{"living":self.create_living_room}, {"dining":self.create_dining_room}, {"bed":self.create_bedroom}]   
        index = randint(0, len(room_options)-1)
        option = _room_options[index]
        while option == "dining":
            if length < 5 or width < 5:
                index = randint(0, len(room_options)-1)
                option = _room_options[index]
            else:
                break
        print(option)
        return room_options, index, option

        # helper func to find doors in rooms with stairs
        # differs by not checking 'wall' next to stairs
    def find_door_from_stairs(self, x1,z1, x2, z2,y, from_stairs):
        doors = []
        air = 0
        door = 64   
        fs_o = from_stairs[1]
        fs_s = from_stairs[2]   
        if not ((fs_o == 1 or fs_o == 3) and (fs_s == 1)): 
            # go east check doorway
            for i in range(abs(x2-x1)):
                block_check = mc.getBlock(x1+i,y,z1)
                if block_check == air or block_check == door:
                    doors.append([Vector2(x1+i,z1), 2]) # doorway has orientation of (2) facing north
                    break
        if not ((fs_o == 2 or fs_o == 4) and (fs_s == 1)):
            # go north check for doorway
            for i in range(abs(z2-z1)):
                block_check = mc.getBlock(x1,y,z1-i)
                if block_check == air or block_check == door:
                    doors.append([Vector2(x1,z1-i), 1]) # facing east
                    break
        if not ((fs_o == 1 or fs_o == 3) and (fs_s == 0)):
            # go east other side
            for i in range(abs(x2-x1)):
                block_check = mc.getBlock(x1+i,y,z2)
                if block_check == air or block_check == door:
                    doors.append([Vector2(x1+i,z2), 4]) #facing south
                    break
        #go north other side
        if not ((fs_o == 2 or fs_o == 4) and (fs_s == 0)):
            for i in range(abs(z2-z1)):
                block_check = mc.getBlock(x2,y,z1-i)
                if block_check == air or block_check == door:
                    doors.append([Vector2(x2,z1-i), 3]) # facing west
                    break
        
        return doors 
    
    # function to find the doors to the room
    def find_door(self, x1,z1, x2, z2,y):
        doors = []
        air = 0
        door = 64   
        # go east check doorway
        for i in range(abs(x2-x1)):
            block_check = mc.getBlock(x1+i,y,z1)
            if block_check == air or block_check == door:
                doors.append([Vector2(x1+i,z1), 2]) # doorway has orientation of (2) facing north
                break
        # go north check for doorway
        for i in range(abs(z2-z1)):
            block_check = mc.getBlock(x1,y,z1-i)
            if block_check == air or block_check == door:
                doors.append([Vector2(x1,z1-i), 1]) # facing east
                break
        # go east other side
        for i in range(abs(x2-x1)):
            block_check = mc.getBlock(x1+i,y,z2)
            if block_check == air or block_check == door:
                doors.append([Vector2(x1+i,z2), 4]) #facing south
                break
        #go north other side
        for i in range(abs(z2-z1)):
            block_check = mc.getBlock(x2,y,z1-i)
            if block_check == air or block_check == door:
                doors.append([Vector2(x2,z1-i), 3]) # facing west
                break
        
        return doors
    
    # clears in front of all doorways dependent on their orientation
    def ensure_doorway_clear(self, locations, y, y2):
        for val in locations:
            location, orientation = val
            if orientation == self.east:
                mc.setBlocks(location.x+1, y, location.z,location.x+1, y2, location.z,block.AIR)     # east
            elif orientation == self.north:
                mc.setBlocks(location.x, y, location.z-1,location.x, y2, location.z-1,block.AIR)    # north
            elif orientation == self.west:
                mc.setBlocks(location.x-1, y, location.z,location.x-1, y2, location.z,block.AIR)     # west
            else:
                mc.setBlocks(location.x, y, location.z+1,location.x, y2, location.z+1,block.AIR)     # south
    
    #function to generate random points along a wall for decoration
    def generate_points(self, start, y, orientation, num_points, length, width):
        points = []
        # orientation = self.choose_orientation(orientation)
        for i in range(num_points):
            if orientation == self.east or orientation == self.west:
                end = Vector2(0, randint(2,width-2))
            else:
                end = Vector2(randint(2,length-2), 0)
            point = [start, end, y, orientation]
            if point not in points:
                points.append(point)
        return points
    
    # function to randomly add a decoration item to a room 
    def add_decoration(self, points):
        options = ["lamp", "flower", "chest", "shelf", "leaves", "crafting", "furnace", "jukebox", "brewing"]
        deco_options = [{"lamp":self.add_lamp},
                        {"flower":self.add_flower}, 
                        {"chest": self.add_chest}, 
                        {"shelf": self.add_shelf},
                        {"leaves": self.add_leaves},
                        {"crafting": self.add_crafting},
                        {"furnace": self.add_furnace},
                        {"jukebox": self.add_jukebox},
                        {"brewing": self.add_brewing}]

        for point in points:
            index = randint(0,len(options)-1)
            opt = options[index]
            start = point[0]
            orientation = point[3]
            end = self.orientate_end(orientation, point[1])
            y = point[2]
            
            mc.postToChat(f"Added {opt} at {start.x-end.x, start.z-end.z, y} facing {orientation}") 
            deco_options[index][opt](start, end, y, orientation)
    # helper function to get the coordinates to use in add functions    
    def initialise_add_coords(self, start, end):
        x1 = start.x
        z1 = start.z
        x2 = x1 - end.x
        z2 = z1 - end.z
        return x1, z1, x2, z2
    # validation function to find doors or add them should there not be a door 
    def get_doors(self, x1, z1, x2, z2, y, from_stairs=[False]):
        if from_stairs[0]:
            doors = self.find_door_from_stairs(x1,z1,x2,z2,y, from_stairs)
        else:
            doors = self.find_door(x1,z1,x2,z2,y)
        if len(doors) != 0:
            doorway_to_orientate_from = randint(0, len(doors)-1)
            doorway, door_orientation = doors[doorway_to_orientate_from] 
        else:
            #safety add door if room has no doors
            try:
                doors = self.add_door(x1,z1,x2,z2,y)
                doorway_to_orientate_from = randint(0, len(doors)-1)
                doorway, door_orientation = doors[doorway_to_orientate_from] 
            except: # don't add a door for example an upstairs room that one big room
                doors = []
                door_orientation = randint(1,4)
                doorway = 0
        
        return doors, doorway, door_orientation

    # def find_front_room(self, x1,z1,x2,z2,y, door_location):
    #     dx1 = door_location.x
    #     dz1 = door_location.z
    #     # go east check doorway
    #     for i in range(abs(x2-x1)-1):
    #         if x1+i == dx1 and z1 == dz1:
    #             return 2 # doorway has orientation of (2) facing north
    #     # go north check for doorway
    #     for i in range(abs(z2-z1)-1):
    #         if x1 == dx1 and z1-i == dz1:
    #             return 1 # facing east
    #     # go east other side
    #     for i in range(abs(x2-x1)-1):
    #         if x1+i == dx1 and z2 == dz1:
    #             return 4 #facing south
    #     #go north other side
    #     for i in range(abs(z2-z1)-1):
    #         if x2 == dx1 and z1-i == dz1:
    #             return 3 # facing west

    #     return 0
    
    # function to clear the block to the side of the stairs start
    def ensure_access_to_stairs(self):
        if self.num_floors > 1 and (self.stairs_start is not None) and (self.stairs_o != 0) and (self.stairs_done): # ensure the stairs have been built before doing this
            orientation = self.stairs_o
            x = self.stairs_start[0].x
            z = self.stairs_start[0].z
            side = self.stairs_start[1]
            y = self.floor_height
            # find block next to stairs based on orientation
            if orientation == self.east:
                if side == 1:
                    z -= 1
                else:
                    z += 1
            elif orientation == self.north:
                if side == 1:
                    x += 1  
                else:
                    x -= 1
            elif orientation == self.west:
                if side == 1:
                    z -= 1
                else:
                    z += 1
            else:
                if side == 1:
                    x += 1  
                else:
                    x -= 1
            
            mc.setBlocks(x, y, z, x, y+2, z ,block.AIR)
    # function to add doors for validation, won't add it along a corner/external wall
    def add_door(self, x1,z1,x2,z2,y):
        # go east check doorway
        if not (x1 >= self.x1 and x1 <= self.x2 and z1 == self.z1):
            door_placement = randrange(1, abs(x2-x1))
            mc.setBlocks(x1+door_placement,y,z1,x1+door_placement,y+1,z1, block.AIR)
            return [[Vector2(x1+door_placement,z1), 2]]      # doorway has orientation of (2) facing north       
        # go north check for doorway
        if not (z1 >= self.z2 and z1 <= self.z1 and x1 == self.x1):
            door_placement = randrange(1, abs(z2-z1))
            mc.setBlocks(x1,y,z1-door_placement,x1,y+1,z1-door_placement, block.AIR) # facing east
            return [[Vector2(x1,z1-door_placement), 1]]
        # go east other side
        if not (x1 >= self.x1 and x1 <= self.x2 and z2 == self.z2):
            door_placement = randrange(1, abs(x2-x1))
            mc.setBlocks(x1+door_placement,y,z2, x1+door_placement,y+1,z2, block.AIR) # facing South
            return [[Vector2(x1+door_placement,z2), 4]]
        #go north other side
        if not (z1 >= self.z2 and z1 <= self.z1 and x2 == self.x2):
            door_placement = randrange(1, abs(z2-z1))
            mc.setBlocks(x2,y,z1-door_placement,x2,y+1,z1-door_placement, block.AIR) # facing west
            return [[Vector2(x2,z1-door_placement), 3]]
        
    # def check_boundary_zone(self,x1,z1, x2, z2):
    #     if self.num_floors < 2 or len(self.boundary_zone) == 0 or self.floor_on > 0:
    #         return x1,z1,x2,z2
    #     bx1 = self.boundary_zone[0].x
    #     bz1 = self.boundary_zone[0].z
    #     bx2 = self.boundary_zone[1].x
    #     bz2 = self.boundary_zone[1].z
    #     # go east check doorway
    #     if (x1 >= bx1 and x1 <= bx2 and z1 == bz1):
    #         z1 += 1    # doorway has orientation of (2) facing north       
    #     # go north check for doorway
    #     if (z1 >= bz2 and z1 <= bz1 and x1 == bx1):
    #         x1 += 1 # facing east

    #     # go east other side
    #     if (x1 >= bx1 and x1 <= bx2 and z2 == bz2):
    #         # facing South
    #         z2 += 1

    #     #go north other side
    #     if (z1 >= bz2 and z1 <= bz1 and x2 == bx2):
    #         x2 -= 1 # facing west


    #     return x1,z1,x2,z2
    
    # function to add the flower
    def add_flower(self, start, end, y, orientation, by_itself=True):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        if by_itself:
            mc.setBlock(x2,y+1,z2, block.FLOWERPOT)
            mc.setBlock(x2,y,z2, block.WOOD_OAK_LOG_Y)
        else:
            mc.setBlock(x2,y+1,z2, block.FLOWERPOT)
    # adds a trapdoor as a shelf
    def add_shelf(self, start, end, y, orientation, part_of_deco=True): # x2, z2 are the end points of the shelf not the room, y should be ground height
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        if part_of_deco:
            mc.setBlocks(x2,y,z2,x2,y,z2, block.TRAPDOOR_TOP_HALF)
        else:
            mc.setBlocks(x1,y,z1,x2,y,z2, block.TRAPDOOR_TOP_HALF)
    # adds a table 
    def add_table(self,start,end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        # randomly choose a fence type for the frame
        fence_type = randint(0,5)
        fences = [block.FENCE, block.FENCE_ACACIA, block.FENCE_BIRCH, block.FENCE_DARK_OAK, block.FENCE_JUNGLE, block.FENCE_SPRUCE]
        # place fence for bottom
        mc.setBlocks(x1,y,z1,x2,y,z2, fences[fence_type])
        # randomly choose a carpet type for the top
        carpet_type = randint(0,4)
        carpet = [block.CARPET_WHITE, block.CARPET_GRAY, block.CARPET_LIGHT_GRAY, block.CARPET_BROWN, block.CARPET_BROWN]
        # place carpets for tabletop
        mc.setBlocks(x1,y+1,z1,x2,y+1,z2, carpet[carpet_type])
    # add a chest
    def add_chest(self, start, end, y, orientation, part_of_deco=True): # y2 is the height of the top 
        y2 = y
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        #orient chest to face the correct direction
        if orientation == self.east: # east
            chest = block.CHEST_EAST
        elif orientation == self.north: # north
            chest = block.CHEST_NORTH
        elif orientation == self.west: # west
            chest = block.CHEST_WEST
        else: # south
            chest = block.CHEST_SOUTH
        if part_of_deco:
            mc.setBlocks(x2,y,z2, x2, y2, z2, chest)
        else:
            mc.setBlocks(x1,y,z1, x2, y2, z2, chest)
    # add lamp
    def add_lamp(self,start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        # randomly choose fence type for post
        fence_type = randint(0,5)
        fences = [block.FENCE, block.FENCE_ACACIA, block.FENCE_BIRCH, block.FENCE_DARK_OAK, block.FENCE_JUNGLE, block.FENCE_SPRUCE]
        # place fence for bottom
        mc.setBlocks(x2,y,z2,x2,y+1,z2, fences[fence_type])
        mc.setBlock(x2,y+2,z2,block.TORCH_UP)
    
    def add_chandelier(self,start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # randomly choose fence type for chandelier
        fence_type = randint(0,5)
        fences = [block.FENCE, block.FENCE_ACACIA, block.FENCE_BIRCH, block.FENCE_DARK_OAK, block.FENCE_JUNGLE, block.FENCE_SPRUCE]
        mc.setBlocks(x1,y,z1,x2,y,z2,fences[fence_type])
        if orientation == self.east:
            mc.setBlock(x1+1,y+1,z1,fences[fence_type])
        elif orientation == self.north:
            mc.setBlock(x1,y+1,z1-1,fences[fence_type])
        elif orientation == self.west:
            mc.setBlock(x1-1,y+1,z1,fences[fence_type])
        else:
            mc.setBlock(x1,y+1,z1+1,fences[fence_type])
        mc.setBlock(x1,y+1,z1,block.TORCH_UP)
        mc.setBlock(x2,y+1,z2,block.TORCH_UP)    
        

    def add_leaves(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        leaves = [block.LEAVES_OAK, block.LEAVES_BIRCH, block.LEAVES_JUNGLE, block.LEAVES_SPRUCE, block.LEAVES2]
        leave_type = randint(0,len(leaves)-1)
        mc.setBlocks(x2,y,z2,x2,y+1,z2,leaves[leave_type])

    def add_crafting(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        mc.setBlock(x2,y,z2,block.CRAFTING_TABLE)
    def add_furnace(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        if orientation == self.east:  # east
            furnace = block.FURNACE_INACTIVE_EAST
        elif orientation == self.north: # north
            furnace = block.FURNACE_INACTIVE_NORTH
        elif orientation == self.west: # west
            furnace = block.FURNACE_INACTIVE_WEST
        else: # south
            furnace = block.FURNACE_INACTIVE_SOUTH
        mc.setBlock(x2,y,z2,furnace)
    def add_jukebox(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        mc.setBlock(x2,y,z2,block.JUKEBOX)
    def add_brewing(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        mc.setBlock(x2,y,z2,block.BREWING_STAND)

    def add_chairs(self, start, end, y, orientation, stairs=False, stair_type=None):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # if not stairs:
            # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        _chairs = ["oak", "spruce", "birch", "jungle", "acacia", "darkoak"]
        chairs = {"oak":[block.STAIRS_WOOD_UP_EAST, block.STAIRS_WOOD_UP_NORTH, block.STAIRS_WOOD_UP_WEST, block.STAIRS_WOOD_UP_SOUTH], 
         "spruce":[block.STAIRS_WOOD_SPRUCE_UP_EAST, block.STAIRS_WOOD_SPRUCE_UP_NORTH, block.STAIRS_WOOD_SPRUCE_UP_WEST, block.STAIRS_WOOD_SPRUCE_UP_SOUTH], 
         "birch":[block.STAIRS_WOOD_BIRCH_UP_EAST, block.STAIRS_WOOD_BIRCH_UP_NORTH, block.STAIRS_WOOD_BIRCH_UP_WEST, block.STAIRS_WOOD_BIRCH_UP_SOUTH], 
         "jungle":[block.STAIRS_WOOD_JUNGLE_UP_EAST, block.STAIRS_WOOD_JUNGLE_UP_NORTH, block.STAIRS_WOOD_JUNGLE_UP_WEST, block.STAIRS_WOOD_JUNGLE_UP_SOUTH], 
         "acacia":[block.STAIRS_WOOD_ACACIA_UP_EAST, block.STAIRS_WOOD_ACACIA_UP_NORTH, block.STAIRS_WOOD_ACACIA_UP_WEST, block.STAIRS_WOOD_ACACIA_UP_SOUTH], 
         "darkoak":[block.STAIRS_WOOD_DARKOAK_UP_EAST, block.STAIRS_WOOD_DARKOAK_UP_NORTH, block.STAIRS_WOOD_DARKOAK_UP_WEST, block.STAIRS_WOOD_DARKOAK_UP_SOUTH]}
        
        
        if stair_type is not None:
            option = stair_type
        else:
            option = _chairs[randint(1,len(_chairs)-1)]
        if orientation == self.east: #east
            stair = chairs[option][0]
        elif orientation == self.north: #north
            stair = chairs[option][1]
        elif orientation == self.west: #west
            stair = chairs[option][2]
        else: #south
            stair = chairs[option][3]

        mc.setBlocks(x1,y,z1,x2,y,z2,stair)
        return option

    # function to get the coordinates out of the dictionary item they are stored in from the building class
    def getCoords(self, room_coords, height= 0):
        key = list(room_coords.keys())
        x1 = key[0][0]
        x2 = room_coords[key[0]][0]
        z1 = key[0][1]
        z2 = room_coords[key[0]][1]
        y = height
        return x1, x2, z1, z2, y

    def add_bed(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        if orientation == self.east: # east
            bed_foot, bed_head = block.BED_FOOT_EAST, block.BED_HEAD_EAST
        elif orientation == self.north: #north
            bed_foot, bed_head = block.BED_FOOT_NORTH, block.BED_HEAD_NORTH
        elif orientation == self.west: #west
            bed_foot, bed_head = block.BED_FOOT_WEST, block.BED_HEAD_WEST
        else: #south
            bed_foot, bed_head = block.BED_FOOT_SOUTH, block.BED_HEAD_SOUTH
        mc.setBlock(x1, y, z1, bed_head)
        mc.setBlock(x2, y, z2, bed_foot)

    # function to create bedroom
    def create_bedroom(self, x1,z1,x2,z2,y, length, width, from_stairs = [False]):
        # get the doors to the room and orientate from one
        doors, doorway, door_orientation = self.get_doors( x1, z1, x2, z2, y, from_stairs)       
        print(doorway, door_orientation)
        num_doors = len(doors)
        orientation = self.choose_orientation(door_orientation)

        # if there is not 4 doors 
        if num_doors != 4: 
            # find the wall that doesn't have door on it
            door_o_opts = [1,2,3,4]
            door_os = [val[1] for val in doors]
            door_os = list(set(door_os) & set(door_o_opts))
            while orientation in door_os:
                orientation = self.choose_orientation(door_os[0])
                if orientation not in door_os:
                    break
                orientation = self.choose_orientation(door_os[0]+1)
                # pass
            print(orientation)

            # initalise x1, z1 to one diagonally across, in the corner rather than the wall
            start = self.orientate_start(x1, z1, x2, z2, orientation)
            # find the middle and place the bed
            if orientation == self.east or orientation == self.west:
                middle = width // 2
                start_b = Vector2(start.x, start.z-middle)
                end_b = self.orientate_end(orientation, Vector2(1,0))
            else:
                middle = length // 2
                start_b = Vector2(start.x+middle, start.z)
                end_b = self.orientate_end(orientation, Vector2(0,1))
            self.add_bed(start_b, end_b, y , orientation)
            
        else:
            # initalise x1, z1 to one diagonally across, in the corner rather than the wall
            start = self.orientate_start(x1, z1, x2, z2, orientation)
            doorway_b = [val[0] for val in doors if val[1] == orientation]
            doorway_b = doorway_b[0]
            print(doorway_b)

            # shift the bed to either the left or right of the door
            if orientation == self.east:
                if randint(0,1) == 1: # go left or right
                    start_b = Vector2(doorway_b.x+1, doorway_b.z-1)
                else:
                    start_b = Vector2(doorway_b.x+1, doorway_b.z+1)
                end_b = self.orientate_end(orientation, Vector2(1,0))
            elif orientation == self.north:
                if randint(0,1) == 1: # go left or right
                    start_b = Vector2(doorway_b.x-1, doorway_b.z-1)
                else:
                    start_b = Vector2(doorway_b.x+1, doorway_b.z-1)
                end_b = self.orientate_end(orientation, Vector2(0,1))
            elif orientation == self.west:
                if randint(0,1) == 1: # go left or right
                    start_b = Vector2(doorway_b.x-1, doorway_b.z-1)
                else:
                    start_b = Vector2(doorway_b.x-1, doorway_b.z+1)
                end_b = self.orientate_end(orientation, Vector2(1,0))
            else:
                if randint(0,1) == 1: # go left or right
                    start_b = Vector2(doorway_b.x-1, doorway_b.z+1)
                else:
                    start_b = Vector2(doorway_b.x+1, doorway_b.z+1)
                end_b = self.orientate_end(orientation, Vector2(0,1))
            self.add_bed(start_b, end_b, y , orientation)

        print(start, "start")
        # add lamps in both corners
        self.add_lamp(start, Vector2(0,0), y, orientation)       
        if orientation == self.east:
            start_l = self.orientate_start(x1,z1,x2,z2, orientation=4)
        elif orientation == self.north:
            start_l = self.orientate_start(x1,z1,x2,z2, orientation=3)
        else:
            start_l = Vector2(x2-1, z2+1)

        self.add_lamp(start_l, Vector2(0,0),y,orientation)

        #decide to place side tables if there is empty space to either side
        if orientation == self.east or orientation == self.west:
            if mc.getBlock(start_b.x,y,start_b.z-1) == 0:
                start_st = Vector2(start_b.x, start_b.z-1)
                self.add_table(start_st, Vector2(0,0), y, orientation)
            if mc.getBlock(start_b.x,y,start_b.z+1) == 0:
                start_st = Vector2(start_b.x, start_b.z+1)
                self.add_table(start_st, Vector2(0,0), y, orientation)
        else:
            if mc.getBlock(start_b.x-1,y,start_b.z) == 0:
                start_st = Vector2(start_b.x-1, start_b.z)
                self.add_table(start_st, Vector2(0,0), y, orientation)
            if mc.getBlock(start_b.x+1,y,start_b.z) == 0:
                start_st = Vector2(start_b.x+1, start_b.z)
                self.add_table(start_st, Vector2(0,0), y, orientation)
        # calculate the number of points for decoration
        if orientation == self.east or orientation == self.west:
            num_points = length // 4
        else:
            num_points = width // 4
        # add decoration
        orientation_d = self.choose_orientation(orientation)
        start_d = self.orientate_start(x1,z1,x2,z2, orientation_d)
        points = self.generate_points(start_d, y, orientation_d, num_points, length, width)
        self.add_decoration(points)
        # add deco in opposite corner to start
        if orientation == self.east or orientation == self.north:
            start_oc = Vector2(x2-1, z2+1)
        elif orientation == self.west:
            start_oc = self.orientate_start(x1,z1,x2,z2, orientation=4)
        else:
            start_oc = self.orientate_start(x1,z1,x2,z2, orientation=3)
        point_oc = [start_oc, Vector2(0,0), y, orientation]
        self.add_decoration([point_oc])
        # self.ensure_doorway_clear(doors, y, y+2)
        # the doors of the room to the master door list to be cleared
        self.all_doors.extend(doors)
        
    def add_stairs(self, start, end, y, y2, orientation, gap=True):
        stair_type = None
        # if there is enough space leave a gap before the stairs
        if gap:
            stairs_length = y2-y
        else:
            stairs_length = (y2-y) - 1
        # add stair and transverse in the next direction
        for i in range(stairs_length):
            mc.setBlocks(start.x,y+1,start.z, start.x, y2+2, start.z, block.AIR) # ensure air above clear
            stair_type = self.add_chairs(start,end, y+i, orientation, stairs=True, stair_type=stair_type)
            if orientation == self.east:
                start.x -= 1
            elif orientation == self.north:
                start.z += 1
            elif orientation == self.west:
                start.x += 1
            else:
                start.z -= 1
        
        # shift start coordinate one back
        if orientation == self.east:
            start.x += 1
        elif orientation == self.north:
            start.z -= 1
        elif orientation == self.west:
            start.x -= 1
        else:
            start.z += 1
            
    
    def create_stairs_room(self,x1,z1,x2,z2,y, base_height, length, width, gap=True):
        doors, doorway, door_orientation = self.get_doors( x1, z1, x2, z2, y)       
        print(doorway, door_orientation)
        orientation = self.choose_orientation(door_orientation) 
        random_chance =  randint(0,1)
        # if there isn't enough space to build along the space axis as the door swap over
        if door_orientation == self.east or door_orientation == self.west:
            if length < self.base_height + 3:
                # random_chance = 1
                door_orientation = orientation
        else:
            if width < self.base_height + 3:
                # random_chance = 1
                door_orientation = orientation
        
        if door_orientation == self.east or door_orientation == self.west: 
            if random_chance == 1: #build stairs left most
                start = self.orientate_start(x1, z1, x2, z2, door_orientation)
                # get plots for stairs facing east
                if door_orientation == self.east:
                    # if there is enough space leave a gap
                    if gap:
                        start_s = Vector2(start.x+1, start.z-(width-1))
                        self.stairs_start = [Vector2(start.x+1, start.z-(width-1)), 0]
                    else:
                        start_s = Vector2(start.x, start.z-(width-1))
                        self.stairs_start = [Vector2(start.x, start.z-(width-1)), 0]
                    # set variables to for boundary and stair orientation to find door from stairs
                    self.stairs_o = 1
                    orientation_s = 3
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 0]
                else: # get plots for stairs facing west
                    orientation_s = 1
                    self.stairs_o = 3
                    if gap:
                        start_s = Vector2(start.x-1, start.z-(width-1))
                        self.stairs_start = [Vector2(start.x-1, start.z-(width-1)), 0]
                    else:
                        start_s = Vector2(start.x, start.z-(width-1))
                        self.stairs_start = [Vector2(start.x, start.z-(width-1)), 0]
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 0]
                # add stairs
                self.add_stairs(start_s, Vector2(0,0), y, base_height, orientation_s, gap)
                # get the rest of the space
                width_s = width - 1
                z2_s = z2 + 2
                # if there is enough space add another room to the stairs
                if width_s > 3:
                    room_options, index, option = self.choose_room(length, width_s)
                    room_options[index][option](x1,z1,x2,z2_s,y,length, width_s, from_stairs)
            # do the same as above except get the plots and build the stairs on the right
            else: #build stairs right most
                start = self.orientate_start(x1, z1, x2, z2, door_orientation)
                if door_orientation == self.east:
                    if gap:
                        start_s = Vector2(start.x+1, start.z)
                        self.stairs_start = [Vector2(start.x+1, start.z), 1]
                    else:
                        start_s = Vector2(start.x, start.z)
                        self.stairs_start = [Vector2(start.x, start.z), 1]
                    self.stairs_o = 1
                    orientation_s = 3
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 1]
                else:
                    if gap:
                        start_s = Vector2(start.x-1, start.z)
                        self.stairs_start = [Vector2(start.x-1, start.z), 1]
                    else:
                        start_s = Vector2(start.x, start.z)
                        self.stairs_start = [Vector2(start.x, start.z), 1]
                    self.stairs_o = 3
                    orientation_s = 1
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 1]
                self.add_stairs(start_s, Vector2(0,0), y, base_height, orientation_s, gap)
                width_s = width - 2
                z1_s = z1 - 2
                if width_s > 3:
                    room_options, index, option = self.choose_room(length, width_s)
                    room_options[index][option](x1,z1_s,x2,z2,y,length, width_s, from_stairs)
        # the same as above except for north/south facing stairs
        else:
            if random_chance == 1: #build stairs left most
                start = self.orientate_start(x1, z1, x2, z2, door_orientation)
                if door_orientation == self.north:
                    if gap:
                        start_s = Vector2(start.x+(length-1), start.z-1)
                        self.stairs_start = [Vector2(start.x+(length-1), start.z-1), 0]
                    else:
                        start_s = Vector2(start.x+(length-1), start.z)
                        self.stairs_start = [Vector2(start.x+(length-1), start.z), 0]
                    self.stairs_o = 2
                    orientation_s = 4
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 0]
                else:
                    orientation_s = 2
                    if gap:
                        start_s = Vector2(start.x+(length-1), start.z+1)
                        self.stairs_start = [Vector2(start.x+(length-1), start.z+1), 0]
                    else:
                        start_s = Vector2(start.x+(length-1), start.z)
                        self.stairs_start = [Vector2(start.x+(length-1), start.z), 0]
                    self.stairs_o = 4
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 0]
                self.add_stairs(start_s, Vector2(0,0), y, base_height, orientation_s, gap) 
                #fill out room
                length_s = length - 1
                x2_s = x2-2
                # self.create_living_room(x1,z1,x2_s,z2,y,length_s, width)
                if length_s > 3:
                    room_options, index, option = self.choose_room(length_s, width)
                    room_options[index][option](x1,z1,x2_s,z2,y, length_s, width, from_stairs)
            else: #build stairs right most
                start = self.orientate_start(x1, z1, x2, z2, door_orientation)
                if door_orientation == self.north:
                    if gap:
                        start_s = Vector2(start.x, start.z-1)
                        self.stairs_start = [Vector2(start.x, start.z-1), 1]
                    else:
                        start_s = Vector2(start.x, start.z)
                        self.stairs_start = [Vector2(start.x, start.z), 1]
                    self.stairs_o = 2
                    orientation_s = 4
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 1]
                else:
                    if gap:
                        start_s = Vector2(start.x, start.z+1)
                        self.stairs_start = [Vector2(start.x, start.z+1), 1]
                    else:
                        start_s = Vector2(start.x, start.z)
                        self.stairs_start = [Vector2(start.x, start.z), 1]
                    self.stairs_o = 4
                    orientation_s = 2
                    self.boundary_zone.extend([self.stairs_start[0], start_s])
                    from_stairs = [True, door_orientation, 1]
                self.add_stairs(start_s, Vector2(0,0), y, base_height, orientation_s, gap)
                length_s = length - 1
                x1_s = x1+2
                if length_s > 3:
                    room_options, index, option = self.choose_room(length_s, width)
                    room_options[index][option](x1_s,z1,x2,z2,y, length_s, width, from_stairs)
        print(self.boundary_zone)


    def add_couch(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        # randomly decide couch type
        _chairs = ["oak", "spruce", "birch", "jungle", "acacia", "darkoak"]
        chairs = {"oak":[block.STAIRS_WOOD_UP_EAST, block.STAIRS_WOOD_UP_NORTH, block.STAIRS_WOOD_UP_WEST, block.STAIRS_WOOD_UP_SOUTH], 
         "spruce":[block.STAIRS_WOOD_SPRUCE_UP_EAST, block.STAIRS_WOOD_SPRUCE_UP_NORTH, block.STAIRS_WOOD_SPRUCE_UP_WEST, block.STAIRS_WOOD_SPRUCE_UP_SOUTH], 
         "birch":[block.STAIRS_WOOD_BIRCH_UP_EAST, block.STAIRS_WOOD_BIRCH_UP_NORTH, block.STAIRS_WOOD_BIRCH_UP_WEST, block.STAIRS_WOOD_BIRCH_UP_SOUTH], 
         "jungle":[block.STAIRS_WOOD_JUNGLE_UP_EAST, block.STAIRS_WOOD_JUNGLE_UP_NORTH, block.STAIRS_WOOD_JUNGLE_UP_WEST, block.STAIRS_WOOD_JUNGLE_UP_SOUTH], 
         "acacia":[block.STAIRS_WOOD_ACACIA_UP_EAST, block.STAIRS_WOOD_ACACIA_UP_NORTH, block.STAIRS_WOOD_ACACIA_UP_WEST, block.STAIRS_WOOD_ACACIA_UP_SOUTH], 
         "darkoak":[block.STAIRS_WOOD_DARKOAK_UP_EAST, block.STAIRS_WOOD_DARKOAK_UP_NORTH, block.STAIRS_WOOD_DARKOAK_UP_WEST, block.STAIRS_WOOD_DARKOAK_UP_SOUTH]}
        
        option = _chairs[randint(1,len(_chairs)-1)]
        if orientation == self.east:
            stair = chairs[option][0]
        elif orientation == self.north:
            stair = chairs[option][1]
        elif orientation == self.west:
            stair = chairs[option][2]
        else:
            stair = chairs[option][3]

        #fill in couch 
        mc.setBlocks(x1,y,z1,x2,y,z2,stair)
        #add corners as sides 
        mc.setBlock(x1,y,z1,block.WOOD_OAK_LOG_Y)
        mc.setBlock(x1,y+1,z1,block.TORCH_UP)
        mc.setBlock(x2,y,z2,block.WOOD_OAK_LOG_Y)
        mc.setBlock(x2,y+1,z2,block.TORCH_UP)
        
    def add_bookshelf(self, start, end, y, orientation):
        x1, z1, x2, z2 = self.initialise_add_coords(start, end)
        # x1, z1, x2, z2 = self.check_boundary_zone(x1, z1, x2, z2)
        # place a bookshlef encased in oak wood for the  living room
        mc.setBlocks(x1,y,z1,x2,y+2,z2,block.WOOD_OAK_LOG_Y)
        mc.setBlocks(x1,y+1,z1,x2,y+1,z2,block.BOOKSHELF)

    def create_living_room(self, x1,z1,x2,z2,y, length, width, from_stairs = [False]):
        doors, doorway, door_orientation = self.get_doors( x1, z1, x2, z2, y, from_stairs)           
        print(doorway, door_orientation)
        orientation = self.choose_orientation(door_orientation)
        # initalise x1, z1 to one diagonally across, in the corner rather than the wall
        start = self.orientate_start(x1, z1, x2, z2, orientation)

        if randint(0,1) == 0: # 50/50 chance to fill couch to corners
            if orientation == self.north or orientation == self.south:
                end_point_c = Vector2(length-1,0)
            else:
                end_point_c = Vector2(0,width-1) 
            end_couch = self.orientate_end(orientation, end_point_c)
            self.add_couch(start,end_couch,y,orientation)
            # self.add_table(Vector2(x1+2,z1-2), Vector2(length-4,1),y,orientation)
        
        else: # leave space in both corners
            if orientation == self.north or orientation == self.south:
                end_point_c = Vector2(length-3,0)
                start_c = Vector2(start.x+1, start.z)
            else:
                end_point_c = Vector2(0,width-3)
                start_c = Vector2(start.x, start.z-1)
            end_couch = self.orientate_end(orientation, end_point_c)
            self.add_couch(start_c,end_couch,y,orientation)
            # self.add_table(Vector2(x1+2,z1-2), Vector2(length-4,1),y,orientation)
        # get the start and end points of the bookshelf based on rooms orientation
        if orientation == self.east:
            end_point_b = Vector2(0,width-3)
            start_b = Vector2(x2-1, start.z-1)
        elif orientation == self.north:
            end_point_b = Vector2(length-3,0)
            start_b = Vector2(start.x+1, z2+1)
        elif orientation == self.west:
            end_point_b = Vector2(0,width-3)
            start_b = Vector2(x1+1, start.z-1)
        else:   
            end_point_b = Vector2(length-3,0)
            start_b = Vector2(start.x+1, z1-1) 
        end_bookshelf = self.orientate_end(orientation, end_point_b)
        self.add_bookshelf(start_b, end_bookshelf,y, orientation)
        # calculate number of points of decoration and add decoration
        if orientation == self.east or orientation == self.west:
            num_points = length // 4
        else:
            num_points = width // 4
        orientation_d = self.choose_orientation(orientation)
        start_d = self.orientate_start(x1,z1,x2,z2, orientation_d)
        points = self.generate_points(start_d, y, orientation_d, num_points, length, width)
        self.add_decoration(points)
        # self.ensure_doorway_clear(doors, y, y+2)
        self.all_doors.extend(doors)

    def choose_table_dimensions(self, length, width):
        # get the length to increment to for the table
        if length > 6:
            t_length = 7
        else:
            t_length = 5
        if width > 6:
            t_width = 7
        else:
            t_width = 5
        return t_length, t_width

    def create_dining_room(self, x1,z1,x2,z2,y, length, width, from_stairs = [False]):
        doors, doorway, door_orientation = self.get_doors(x1, z1, x2, z2, y, from_stairs)       
        print(doorway, door_orientation)
        orientation_t = 1
        t_length, t_width = self.choose_table_dimensions(length, width)
        start = self.orientate_start(x1, z1, x2, z2, orientation_t)
        # add the main table 
        start_mt = Vector2(start.x+((t_length//2)), start.z-((t_width//2)))   
        print(start_mt)     
        end_mt = self.orientate_end(orientation_t, Vector2(length-t_length,width-t_width))
        self.add_table(start_mt, end_mt, y, orientation_t)
        # get the startc coords for each chair
        start_ce = Vector2(start_mt.x-1, start_mt.z)
        start_cw = Vector2(start_mt.x+(length-t_length)+1, start_mt.z)
        start_cn = Vector2(start_mt.x, start_mt.z+1)
        start_cs = Vector2(start_mt.x, start_mt.z-(width-t_width)-1)
        # print(start_ce, start_cw, start_cn, start_cs)
        type = None
        side_not_done = True
        # 1/4 chance to not build these chairs
        if randint(1,4) != 2:
            side_not_done = False
            #place chairs east and west of the table
            end_cw = self.orientate_end(3, Vector2(0, width-t_width))
            type = self.add_chairs(start_cw, end_cw, y, orientation=3, stair_type=type)
            end_ce = self.orientate_end(1, Vector2(0, width-t_width))
            self.add_chairs(start_ce, end_ce, y, orientation=1, stair_type=type)
        # if the east and west hasn't been done place chairs north/ south
        if side_not_done:
            end_cn = self.orientate_end(2, Vector2(length-t_length, 0))        
            type = self.add_chairs(start_cn, end_cn, y, orientation=2, stair_type=type)
            end_cs = self.orientate_end(4, Vector2(length-t_length, 0))
            self.add_chairs(start_cs, end_cs, y, orientation=4, stair_type=type)
        # else 1/4 chance to north have the north/south chairs
        elif randint(1,4) != 2:
            end_cn = self.orientate_end(2, Vector2(length-t_length, 0))        
            type = self.add_chairs(start_cn, end_cn, y, orientation=2, stair_type=type)
            end_cs = self.orientate_end(4, Vector2(length-t_length, 0))
            self.add_chairs(start_cs, end_cs, y, orientation=4, stair_type=type)
        # if there is enough height add a chandelier
        if self.base_height == 3:
            middle_z = width // 2
            middle_x = length // 2
            start_ch = Vector2(start.x+middle_x-1, start.z-middle_z)
            end_ch = self.orientate_end(orientation_t, Vector2(2,0))
            # check the heights as they differ per floor
            if self.num_floors == 2:
                if self.floor_on == 0:
                    height = y+self.base_height - 1
                else:
                    height = y+self.base_height
            else:
                height = y+self.base_height
            self.add_chandelier(start_ch, end_ch,height,orientation_t)
        # self.ensure_doorway_clear(doors, y, y+2)
        self.all_doors.extend(doors)
    
    def clear_above_stairs(self, y, y2):
        # set air above the stairs to ensure it's clear
        if self.num_floors > 1 and (self.stairs_done):
            bx1 = self.boundary_zone[0].x
            bz1 = self.boundary_zone[0].z
            bx2 = self.boundary_zone[1].x
            bz2 = self.boundary_zone[1].z
            mc.setBlocks(bx1, y, bz1, bx2, y2, bz2, block.AIR)


        

#TEST CASE
if __name__ == "__main__":
    tp = mc.player.getTilePos()
    x = tp.x
    z = tp.z
    y = tp.y
    f = Furnish([[{(x,z):(x+14,z-10)}]], 1, y, 3,[x,z,x+14,z-10])
    # {(1025, -1066):(1033, -1076)}], [{(1025, -1066):(1033, -1076)}]], 2, 155, 3, [1025, -1066, 1033, -1076]
    # f.find_door(884,-1179,889, -1186,104)
    # f.create_stairs_room(x, z, x+7, z+5, y, y+4, 6, 4)
    # {(x,z):(x+4, z-15)}, {(x+4, z):(x+12, z-15)}]
    # {(x,z):(x+8, z-6)}, {(x, z-6):(x+8, z-15)},
    # , {(x, z-6):(x+8, z-15)}
    # print(x,y,z)
    # test = mc.getBlock(x,y,z)
    # print(test)
    # mc.setBlock(x+1,y,z,96,8)