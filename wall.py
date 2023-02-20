from mcpi import block
from mcpi.minecraft import Vec3, Minecraft

"""
Door value of -1 means no door, 0 is air, 1 is wooden door
Windows can be toggled on or off with windows param
If no base_height is given, function will calculate the base_height using mc.getHeight()
"""


class Wall:
    def __init__(self, mc, start_point, end_point, height=6,
                 wall_type=block.STONE, windows=True, base_height=None, door=-1):
        self.mc = mc
        self.start_point = start_point
        self.end_point = end_point
        self.height = height
        self.type = wall_type
        self.base_height = base_height
        self.door = door
        self.door_coords = None

        self.build(mc, start_point, end_point, wall_type, height, windows, base_height, door)

    def build(self, mc, start, end, block_type, height, windows, base_height, door):
        """
        Bresenham's Line Algorithm
        Produces a list of tuples from start and end points
        (This code is adapted from an implementation on roguebasin.com)
        """
        # Variables to be manipulated

        # Setup initial conditions
        x1, y1, z1 = Vec3(start.x, start.y, start.z)
        x2, y2, z2 = Vec3(end.x, end.y, end.z)
        dx = x2 - x1
        dy = z2 - z1
        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)
        # Rotate line
        if is_steep:
            x1, z1 = z1, x1
            x2, z2 = z2, x2
        # Swap start and end points if necessary
        if x1 > x2:
            x1, x2 = x2, x1
            z1, z2 = z2, z1
        # Recalculate differentials
        dx = x2 - x1
        dy = z2 - z1
        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if z1 < z2 else -1
        # Iterate over bounding box generating points between start and end
        z = z1

        # Adjust window_spacing based on wall length
        wall_length = abs(dx**2 + dy**2)
        if wall_length % 2 == 0:
            if wall_length < 6:
                window_spacing = 2
            elif wall_length < 15:
                window_spacing = 4
            else:
                window_spacing = 6
        else:
            if wall_length < 5:
                window_spacing = 1
            elif wall_length < 15:
                window_spacing = 3
            else:
                window_spacing = 5
        # Iterable length counter and window_placed check (gives 2x2 window)
        length = 0
        window_placed = 0
        for x in range(x1, x2 + 1):
            coord = (z, x) if is_steep else (x, z)
            if not base_height:
                base = mc.getHeight(coord[0], coord[1]) + 1
            else:
                base = base_height
            # Check there isn't already a wall in place
            if mc.getBlockWithData(coord[0], y1, coord[1]) != block_type:
                # Place column with window
                # TODO: Add window randomness back in?
                if windows and length > window_spacing or window_placed > 0:
                    # Add a floor block
                    mc.setBlock(coord[0], base, coord[1], block_type)
                    base += 1
                    # Add two window blocks
                    for i in range(2):
                        mc.setBlock(coord[0], base, coord[1], block.GLASS)
                        base += 1
                    # Finish the column
                    for i in range(3, height + 1):
                        mc.setBlock(coord[0], base, coord[1], block_type)
                        base += 1
                    # Reset length counter
                    length = 0
                    window_placed += 1
                    if window_placed == 2:
                        window_placed = 0
                else:  # Place specified block
                    for i in range(height + 1):
                        mc.setBlock(coord[0], base, coord[1], block_type)
                        base += 1
            # If needed, leave an air-space for door and save its coordinates:
            if door >= 0 and x == ((x1 + x2) // 2):
                self.door_coords = [(coord[0], base_height, coord[1]), (coord[0], base_height + 1, coord[1])]

            length += 1

            error -= abs(dy)
            if error < 0:
                z += ystep
                error += dx

        # After wall is built, if door > 0, add a doorway midway through wall, type is dependent on number
        if door >= 0:
            # List of door_types as tuples
            # TODO: Add exception if door value is longer than DOOR_TYPE list - GEK
            door_type = [(0, 0), (block.DOOR_WOOD.withData(3), block.DOOR_WOOD.withData(11))]
            door_bottom, door_top = door_type[door]
            # TODO: Add different types of doors - GEK.
            mc.setBlock(self.door_coords[1], door_top)
            mc.setBlock(self.door_coords[0], door_bottom)

# TEST CASE
if __name__ == "__main__":
    # create minecraft connection
    mc = Minecraft.create()

    player_pos = mc.player.getTilePos()
    other_pos = Vec3(player_pos.x + 250, player_pos.y, player_pos.z + 250)

    wall = Wall(mc, player_pos, other_pos, windows=False)
