from math import sqrt

class Vector2:
	__slots__ = 'x', 'z'
	def __init__(self, x, z):
		self.x = x
		self.z = z

	def __str__(self):
		return f'({self.x}, {self.z})'

	def __repr__(self) -> str:
		return self.__str__()

	def __iter__(self):
		yield self.x
		yield self.z

	def __add__(self, other):
		if type(other) in [int, float]:
			return Vector2(self.x + other, self.z + other)
		if type(other) is Vector2:
			return Vector2(self.x + other.x, self.z + other.z)
		raise TypeError(f'Cannot multiply Vector2 by {type(other)}')

	def __mul__(self, other):
		if type(other) in [int, float]:
			return Vector2(self.x * other, self.z * other)
		if type(other) is Vector2:
			return Vector2(self.x * other.x, self.z * other.z)
		raise TypeError(f'Cannot multiply Vector2 by {type(other)}')

	def extended_by(self, offset):
		"""
		Returns a Rect with self as one corner, and the other corner
		as an offset.
		"""
		if type(offset) in [int, float]:
			offset = Vector2(offset, offset)
		if type(offset) is Vector2:
			return Rectangle(self, self + offset)
		raise TypeError(f'Cannot extend Pair by {type(offset)}')

	def extended_to(self, other : 'Vector2'):
		"""
		Returns a Rect with self as one corner and the second Vector2 as the
		other corner.
		"""
		if type(other) is Vector2:
			return Rectangle(self, other)
		raise TypeError(f'Cannot extend Pair by {type(other)}')

	def range(self):
		return (self.x, self.z)

	def asXY_(self, z):
		return Vector3(self.x, self.z, z)

	def asX_Z(self, y):
		return Vector3(self.x, y, self.z)

	def length(self):
		sqrt(self.x * self.x + self.z * self.z)


class Vector3:
	__slots__ = 'x', 'y', 'z'
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return f'({self.x}, {self.y}, {self.z})'

	def __repr__(self) -> str:
		return self.__str__()

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z

	def asXY(self):
		return Vector2(self.x, self.y)

	def asXZ(self):
		return Vector2(self.x, self.z)

	def asYZ(self):
		return Vector2(self.y, self.z)

	def length(self):
		sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

class Rectangle:
	"""
	Represents a rectangle, on the xz plane by default, but can be projected onto the other planes.
	"""
	__slots__ = 'v1', 'v2', 'x0', 'x1', 'z0', 'z1', 'small_corner', 'large_corner', 'width', 'height', 'half', 'centre'
	def __init__(self, v1 : Vector2, v2 : Vector2):
		"""
		v1 and v2 represent the two corners of the rectangle.
		They can be in any order, but will be internally represented going from
		smaller x/z to higher x/z (aka the small and large corner, respectively).
		"""

		self.x0 = min(v1.x, v2.x)
		self.x1 = max(v1.x, v2.x)
		self.z0 = min(v1.z, v2.z)
		self.z1 = max(v1.z, v2.z)
		
		self.small_corner = Vector2(self.x0, self.z0)
		self.large_corner = Vector2(self.x1, self.z1)

		self.width = self.large_corner.x - self.small_corner.x + 1 # in minecraft, the bounds are inclusive, so we add 1
		self.height = self.large_corner.z - self.small_corner.z + 1

		self.half = Vector2(self.width / 2.0, self.height / 2.0)
		self.centre = Vector2(self.small_corner.x + self.half.x, self.small_corner.z + self.half.z)

	def __str__(self):
		return f'{self.small_corner} to {self.large_corner}'

	def __repr__(self) -> str:
		return self.__str__()
	
	def __add__(self, offset) -> 'Rectangle':
		if type(offset) in [int, float]:
			offset = Vector2(offset, offset)
			return Rectangle(self.small_corner + offset, self.large_corner + offset)
		if type(offset) is Vector2:
			return Rectangle(self.small_corner + offset, self.large_corner + offset)
		raise TypeError(f'Cannot add {type(offset)} to Rectangle')

	def intersects(self, other) -> bool:
		dx = other.centre.x - self.centre.x
		px = (other.half.x + self.half.x) - abs(dx)

		if px <= 0:
			return False

		dz = other.centre.z - self.centre.z
		pz = (other.half.z + self.half.z) - abs(dz)

		if pz <= 0:
			return False

		return True

	def contains(self, other) -> bool:
		if type(other) is Rectangle:
			return self.x0 <= other.x0 and	\
				   self.x1 >= other.x1 and	\
				   self.z0 <= other.z0 and	\
				   self.z1 >= other.z1
		if type(other) is Vector2:
			return self.x0 <= other.x and	\
				   self.x1 >= other.x and	\
				   self.z0 <= other.z and	\
				   self.z1 >= other.z

	def clamp(self, other: Vector2) -> Vector2:
		if self.contains(other):
			return other
		else:
			clamped_x = self.x0 if other.x < self.x0 else self.x1
			clamped_z = self.z0 if other.z < self.z0 else self.z1
			return Vector2(clamped_x, clamped_z)

	def area(self):
		return self.width * self.height

	def expanded_by(self, amount):
		if type(amount) in [int, float]:
			amount = Vector2(amount, amount)
		if type(amount) is Vector2:
			return Rectangle(Vector2(self.small_corner.x - amount.x,
									 self.small_corner.z - amount.z),
							 Vector2(self.large_corner.x + amount.x,
									 self.large_corner.z + amount.z))
		raise TypeError(f'Cannot expand Rect by {type(amount)}')

	def x_range(self):
		return self.small_corner.x, self.large_corner.x

	def z_range(self):
		return self.small_corner.z, self.large_corner.z

		

# class Box:
# 	"""
# 	Represents a cuboid.
# 	"""
# 	def __init__(self, v1 : Vector3, v2 : Vector3):
# 		"""
# 		v1 and v2 represent the two corners of the box.
# 		They can be in any order, but will be internally represented going from
# 		smaller x/y/z to higher x/y/z (aka the small and large corner, respectively).
# 		"""

# 		self.x0 = min(v1.x, v2.x)
# 		self.x1 = max(v1.x, v2.x)
# 		self.y0 = min(v1.y, v2.y)
# 		self.y1 = max(v1.y, v2.y)
# 		self.z0 = min(v1.z, v2.z)
# 		self.z1 = max(v1.z, v2.z)
		
# 		self.small_corner = Vector2(self.x0, self.z0)
# 		self.large_corner = Vector2(self.x1, self.z1)

# 		self.width = self.large_corner.x - self.small_corner.x + 1 # in minecraft, the bounds are inclusive, so we add 1
# 		self.height = self.large_corner.z - self.small_corner.z + 1

# 		self.half = Vector2(self.width / 2.0, self.height / 2.0)
# 		self.centre = Vector2(self.small_corner.x + self.half.x, self.small_corner.z + self.half.z)

# 	def __str__(self):
# 		return f'{self.small_corner} to {self.large_corner}'

# 	def __repr__(self) -> str:
# 		return self.__str__()

# 	def intersects(self, other) -> bool:
# 		dx = other.centre.x - self.centre.x
# 		px = (other.half.x + self.half.x) - abs(dx)

# 		if px <= 0:
# 			return False

# 		dz = other.centre.z - self.centre.z
# 		pz = (other.half.z + self.half.z) - abs(dz)

# 		if pz <= 0:
# 			return False

# 		return True

# 	def area(self):
# 		return self.width * self.height

# 	def expanded_by(self, amount):
# 		if type(amount) in [int, float]:
# 			amount = Vector2(amount, amount)
# 		if type(amount) is Vector2:
# 			return Rectangle(Vector2(self.small_corner.x - amount.x,
# 									 self.small_corner.z - amount.z),
# 							 Vector2(self.large_corner.x + amount.x,
# 									 self.large_corner.z + amount.z))
# 		raise TypeError(f'Cannot expand Rect by {type(amount)}')

# 	def x_range(self):
# 		return self.small_corner.x, self.large_corner.x

# 	def z_range(self):
# 		return self.small_corner.z, self.large_corner.z