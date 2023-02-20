from mcpi.minecraft import Minecraft
from mcpi import block

mc = Minecraft.create()

playerTilePos = mc.player.getTilePos()

### EXAMPLE 1 ###

# Floor
mc.setBlocks(playerTilePos.x + 2, playerTilePos.y, playerTilePos.z - 2, playerTilePos.x + 6, playerTilePos.y, playerTilePos.z + 2, block.STONE_BRICK)

# Walls
mc.setBlocks(playerTilePos.x + 2, playerTilePos.y, playerTilePos.z - 1, playerTilePos.x + 2, playerTilePos.y + 2, playerTilePos.z + 2, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 6, playerTilePos.y, playerTilePos.z - 1, playerTilePos.x + 6, playerTilePos.y + 2, playerTilePos.z + 2, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 3, playerTilePos.y, playerTilePos.z - 1, playerTilePos.x + 3, playerTilePos.y + 2, playerTilePos.z - 1, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 5, playerTilePos.y, playerTilePos.z - 1, playerTilePos.x + 5, playerTilePos.y + 2, playerTilePos.z - 1, block.BRICK_BLOCK)

# Door
mc.setBlock(playerTilePos.x + 4, playerTilePos.y + 2, playerTilePos.z - 2, block.DOOR_WOOD.withData(8))
mc.setBlock(playerTilePos.x + 4, playerTilePos.y + 1, playerTilePos.z - 2, block.DOOR_WOOD.withData(3))


### EXAMPLE 2 ###

# Floor
mc.setBlocks(playerTilePos.x + 12, playerTilePos.y, playerTilePos.z - 2, playerTilePos.x + 16, playerTilePos.y, playerTilePos.z + 2, block.STONE_BRICK)

# Walls
mc.setBlocks(playerTilePos.x + 13, playerTilePos.y, playerTilePos.z - 2, playerTilePos.x + 16, playerTilePos.y + 2, playerTilePos.z - 2, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 13, playerTilePos.y, playerTilePos.z + 2, playerTilePos.x + 16, playerTilePos.y + 2, playerTilePos.z + 2, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 13, playerTilePos.y, playerTilePos.z - 1, playerTilePos.x + 13, playerTilePos.y + 2, playerTilePos.z - 1, block.BRICK_BLOCK)
mc.setBlocks(playerTilePos.x + 13, playerTilePos.y, playerTilePos.z + 1, playerTilePos.x + 13, playerTilePos.y + 2, playerTilePos.z + 1, block.BRICK_BLOCK)

# Door
mc.setBlock(playerTilePos.x + 13, playerTilePos.y + 2, playerTilePos.z, block.DOOR_WOOD.withData(8))
mc.setBlock(playerTilePos.x + 13, playerTilePos.y + 1, playerTilePos.z, block.DOOR_WOOD.withData(0))
