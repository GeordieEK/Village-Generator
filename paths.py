# path_finder() was adapted from the A* algorithm outlined here
# https://www.redblobgames.com/pathfinding/a-star/introduction.html
#
# Much of the code was changed to make it useable in minecraft.
# Only the fundamental aspects of an A* search algorithm are kept consistent
# with the website. 
#
# M. Martinuzzo/s3850470/RMITMatthewMartinuzzo

from secrets import choice
from webbrowser import get
import block

import numpy as np
from sklearn.linear_model import LinearRegression
from queue import PriorityQueue
from heightmap import Heightmap
from time import sleep

from utils import *
from building import *

from brush import *
from village import Village

class Paths:
    def __init__(self, village: Village):
        self.village = village
        self.doors = [(plot.door_mat.x, plot.door_mat.z) for plot in self.village.plots if plot.requires_path]
    
    def construct(self):
        self.draw_main_road()
        self.draw_side_roads()

    def draw_main_road(self):
        """Use LinearRegression to draw a road through the village"""
        self.village.mc.postToChat("Calculating Main Road")

        # reshape door coordinate data for sklearn Linear Regression Modelling
        x_np = np.array([x[0] for x in self.doors]).reshape((-1, 1))
        z_np = np.array([x[1] for x in self.doors])
        model = LinearRegression().fit(x_np, z_np)

        intercept = model.intercept_
        gradient = model.coef_[0]
        xmin = self.village.bounds.small_corner.x
        xmax = self.village.bounds.large_corner.x

        zmin = int(xmin * gradient + intercept)
        zmax = int(xmax * gradient + intercept)

        start = (xmin, zmin)
        end = (xmax, zmax)

        result = None
        self.main_road = None
        while result is None:
            try:
                start_block = self.village.map._map[start][1]
                end_block = self.village.map._map[start][1]
                while start_block == block.WATER or start_block == block.WATER_STATIONARY or start_block == WATER_FLOWING:
                    xmin += 1
                    zmin = int(xmin * gradient + intercept)
                    start = (xmin, zmin)
                    start_block = self.village.map._map[start][1]
                while end_block == block.WATER or end_block == block.WATER_STATIONARY or end_block == WATER_FLOWING:
                    xmax -= 1
                    zmax = int(xmin * gradient + intercept)
                    end = (xmax, zmax)
                    end_block = self.village.map._map[start][1]
                result, self.main_road = self.path_finder(start, end, self.village.map)
            except KeyError:
                xmin += 1
                xmax -= 1
                zmin = int(xmin * gradient + intercept)
                zmax = int(xmax * gradient + intercept)
                
                start = (xmin, zmin)
                end = (xmax, zmax)
            
        self.draw_paths(Pattern(EASY_PATH), self.main_road)
        self.village.mc.postToChat("Main Road Placed")

    def draw_paths(self, pattern, path):
        """Takes a list of paths and translates it for use with Brush Class"""
        
        path_brush = Brush(self.village.mc, pattern) 
        path_iterations = len(path) - 1
        
        # iterate through path, use brush to draw one segment blocks
        for i in range(path_iterations):
            ax = path[i][0]
            az = path[i][1]
            
            bx = path[i+1][0]
            bz = path[i+1][1]

            a_height = self.village.map.height(ax, az)
            b_height = self.village.map.height(bx, bz)
            x_direction = bx-ax
            z_direction = bz-az
            
            if x_direction == 1:
                path_brush.face(Facing.SOUTH)
                path_brush.draw(ax, a_height, az, bx, b_height, bz, False)
            elif x_direction == -1:
                path_brush.face(Facing.SOUTH)
                path_brush.draw(ax, a_height, az, bx, b_height, bz, False)
            elif z_direction == 1:
                path_brush.face(Facing.EAST)
                path_brush.draw(ax, a_height, az, bx, b_height, bz, False)
            elif z_direction == -1:
                path_brush.face(Facing.EAST)
                path_brush.draw(ax, a_height, az, bx, b_height, bz, False)
    
    def draw_side_roads(self):
        """Draws side roads by finding closest coordinate to main road"""
        self.village.mc.postToChat("Calculating Side Roads")
        for door in self.doors:
            self.village.mc.postToChat("Calculating Road:")
            self.village.mc.postToChat(str(door))
            x_coord = door[0]
            z_coord = door[1]
            end = (x_coord, z_coord)
            found_location = True
            for coord in self.main_road:
                if coord[0] == x_coord:
                    end = coord
                    found_location = False
                    break
            if found_location:
                end = choice(self.main_road)
            _, path = self.path_finder((x_coord, z_coord), end, self.village.map)
            self.draw_paths(Pattern([[[[Block(208, 0)]]]]), path)
        self.village.mc.postToChat("Side Roads Placed")
        
    def path_finder(self, start_coord: tuple, end_coord: tuple, height_map: Heightmap):
        """Finds the shortest path between two points on a map using A* algorithm

        Args:
            start_coord (x, z): The starting coordinates of the path as a tuple
            end_coord (x, z): The ending coordinates of the path as a tuple
            height_map (dict): The height map of the area as a dictionary {(x, y): height, blockid}
            mc : API connection to Minecraft

        Returns:
            Creates a path between the two points and returns the updated map with path
        
        Example:
            path_finder((0, 0), (10, 10), height_map)
            Finds the shortest path between (0, 0) and (10, 10) on the map
        """

        def heuristic(start_coord: tuple, end_coord: tuple):
            """Calculates the heuristic distance between two points utilizing Manhattan distance"""
            return abs(start_coord[0] - end_coord[0]) + abs(start_coord[1] - end_coord[1])

        def neighbours(coord, height_map: Heightmap):
            """Returns a list of neighbouring coordinates in 8 directions to input coord that are within the map"""
            neighbours = []
            x, z = coord
            FORBIDDEN_PATHS = [block.CUSTOM_PATH.id]
            # up
            if (x + 1, z) in height_map._map and height_map.block(x + 1, z).id not in FORBIDDEN_PATHS:
                neighbours.append((x + 1, z))
            # down
            if (x - 1, z) in height_map._map and height_map.block(x - 1, z).id not in FORBIDDEN_PATHS:
                neighbours.append((x - 1, z))
            # right
            if (x, z + 1) in height_map._map and height_map.block(x, z + 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x, z + 1))
            # left
            if (x, z - 1) in height_map._map and height_map.block(x, z - 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x, z - 1))
            # up right
            if (x + 1, z + 1) in height_map._map and height_map.block(x + 1, z + 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x + 1, z + 1))
            # up left
            if (x + 1, z - 1) in height_map._map and height_map.block(x + 1, z - 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x + 1, z - 1))
            # down right
            if (x - 1, z + 1) in height_map._map and height_map.block(x - 1, z + 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x - 1, z + 1))
            # down left
            if (x - 1, z - 1) in height_map._map and height_map.block(x - 1, z - 1).id not in FORBIDDEN_PATHS:
                neighbours.append((x - 1, z - 1))
            return neighbours

        def cost_next(coord: tuple, next_coord: tuple, height_map: Heightmap):
            """Returns the cost of moving from coord to next_coord
            The cost is exponentially higher if the next_coord is higher than coord based on HEIGHT_COST_FACTOR"""
            x, z = coord[0], coord[1]
            x_next, z_next = next_coord[0], next_coord[1]
            next_block = height_map._map[x_next, z_next][1]
            WATER_COST = 0
            BASE_COST = 1
            HEIGHT_COST_FACTOR = 3
            if next_block == block.WATER or next_block == block.WATER_STATIONARY or next_block == WATER_FLOWING:
                WATER_COST = 10
            return BASE_COST +  HEIGHT_COST_FACTOR**abs(height_map.height(x, z) - height_map.height(x_next, z_next)) + WATER_COST
        
        # Initial setup for A* algorithm
        frontier = PriorityQueue()
        frontier.put((0, start_coord))
        came_from = {}
        cost_so_far = {}
        came_from[start_coord] = None
        cost_so_far[start_coord] = 0
        
        while not frontier.empty():
            currentData = frontier.get()
            current = currentData[1]
            if current == end_coord:
                break
            for next in neighbours(current, height_map):
                new_cost = cost_so_far[current] + cost_next(current, next, height_map)
                if next not in came_from or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(next, end_coord)
                    frontier.put((priority, next))
                    came_from[next] = current

        # Reconstructs the path from the end to the start
        path = []
        current = end_coord
        while current != start_coord:
            path.append(current)
            current = came_from[current]
        path.append(current)

        return height_map, path