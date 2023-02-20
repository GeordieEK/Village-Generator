# Minecraft Village - School Project

## Video is [HERE](https://youtu.be/aweZiwTiCUw)

## How to use

Running main.py will start construction of a Village at the player's location.
Most biomes and terrains should work fine, however ocean biomes will take a very
long time to expand and find land. Pathfinding through ocean or ice/island
biomes works but is not very pretty.

## Dependencies

- scikit-learn https://scikit-learn.org/stable/install.html
- numpy https://numpy.org/install/

## Server querying issues

The fast query is not guaranteed to always return all requested data: we
did experience some cases where there was missing block/height data, which
results in KeyErrors if we try to build or path through that block.

We tweaked the number of threads and requests to reduce this, and it seemed to
only occur for some of us (slower computers?) but we have not found a stable
solution for this other than restarting the program.

# Student contributions

## Benjamin Grayland (s3927837, marmaladian)

- 25-30%
- adapt fast query code for Python 3/mcpi (threaded and batched getblock/getheight requests)
- flat land search algorithms (this approach was abandoned for more destructive terraforming)
- ASCII height map renderer (debugging tool)
- building plot placement and set up
- Gaussian blur terraforming
- brush/pattern system

## Matthew Martinuzzo (s3850470, RMITMatthewMartinuzzo, matthewmartinuzzo)

- 25%
- implement a\* algorithm for pathing
- utilize path tool with a\*
- filtered height map creation from fast_query setup
- flat land search algorithms (abandoned)
- skeleton code for buildings
- skeleton code for recursive rooms
- a\* for pathing
- filtered height map

## Geordie Elliot-Kerr (s3465651, GeordieEK)

- 25%
- implement Bresenham's line algorithm
- wall objects and their customisation
- improve and finalise recursive rooms
- improve and finalise buildings, including overall design, columns, windows etc.
- design pools and gardens
- material randomisation
- some minor additional work on utilities
- final video direction & editing

## Maximus Alexander Dionyssopoulos (s3943811)

- 25%
- created and implemented roof style 1 and 2
- furnished rooms
- created and implemented:
  - stairs between floors
  - living room
  - bedroom
  - dining room
  - decoration pieces for rooms
- implemented randomisation of rooms through:
  - materials
  - orientation

## References/other code used

- A\* algorithm based on implementation by Amit Patel <https://www.redblobgames.com/pathfinding/a-star/introduction.html>
- Fast block queries based on implementation by Joseph Reynolds <https://github.com/joseph-reynolds/mcpi_fast_query>
- Bresenham's line drawing algorithm
