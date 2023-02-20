# This module is based on mcpi_fast_query by joseph-reynolds
# https://github.com/joseph-reynolds/mcpi_fast_query
#
# Some changes were made to get it working with Python 3,
# and functions added to query the surface of the world, rather
# than 3D volumes of blocks or a flat surface.
#
# B. Grayland/s3927837/marmaladian
import collections
import select
import socket
import threading
import queue
from block import *
from utils import *

class Cuboid:
	"""A cuboid represents a 3-dimensional rectangular area

	The constructor takes ranges along the x, y, and z axis,
	where each range is a tuple(min, max) of world coordinates.
	Ranges are integers and are used like the Python built-in range
	function where the second number is one past the end.  Specifically,
	to get a single point along an axis, use something like tuple(0, 1).

	Examples:
	  # A point at (100,12, 5)
	  >>> point = Cuboid((100,101), (12,13), (5,6))
	  
	  # An 11 by 11 square centered around (0,0):
	  >>> c = Cuboid((-5, 6), (0, 1), (-5, 6))
	  >>> c.x_range
	  (-5, 6)
	  >>> g = c.generate()
	  >>> for point in g: print(p)
	"""
	def __init__(self, x_range, y_range, z_range):
		if x_range[0] >= x_range[1]: raise RuntimeError("bad x")
		if y_range[0] >= y_range[1]: raise RuntimeError("bad y")
		if z_range[0] >= z_range[1]: raise RuntimeError("bad z")
		self.x_range = x_range
		self.y_range = y_range
		self.z_range = z_range
	
	def __repr__(self):
		return "(%s, %s, %s)" % (str(self.x_range), str(self.y_range), str(self.z_range))
	
	def generate(self):
		for x in range(*self.x_range):
			for y in range(*self.y_range):
				for z in range(*self.z_range):
					yield (x, y, z)

	def generate_xz(self):
		for x in range(*self.x_range):
			for z in range(*self.z_range):
				yield (x, z)

	def total_blocks(self):
		return ((self.x_range[1] - self.x_range[0]) *
				(self.y_range[1] - self.y_range[0]) *
				(self.z_range[1] - self.z_range[0]))


"""query_blocks

Purpose:
  This generator is for getting a lot of data from the Minecraft server
  quickly.  For example, if you want data from a thousand blocks you
  could call getBlock for each block, but that would take a long time.
  This function essentially calls getBlock for many blocks at the same
  time, thus improving throughput.
  If you want data for just a few blocks, prefer to use getBlock.

  The following query functions are supported:
	world.getBlock(x,y,z) -> blockId
	world.getBlockWithData(x,y,z) -> blockId,blockData
	world.getHeight(x,z) -> y

  Parameters:
	requests
			An iterable of coordinate tuples.  See the examples.
			Note that this will be called from different threads.
	fmt
			The request format string, one of:
				world.getBlock(%d,%d,%d)
				world.getBlockWithData(%d,%d,%d)
				world.getHeight(%d,%d)
	parse_fn
			Function to parse the results from the server, one of:
				int
				tuple(map(int, ans.split(",")))
	thread_count
			Number of threads to create.

  Generated values:
	tuple(request, answer), where
	  request - is a value from the "requests" input parameter
	  answer - is the response from the server, parsed by parse_fn    

Query the Minecraft server quickly using two techniques:
 1. Create worker threads, each with its own socket connection.
 2. Each thread sends requests into the socket without waiting
	for responses.  Responses are then matched with requests.

The low-level design notes:
 - This uses a straightforward thread model
 - Creating more than 50 threads gets expensive.
 
 - The main thread creates the following
	 request_lock = threading.Lock()  # Serialize access to requests
	 answer_queue = queueing.Queue()  # Get answers from threads
	 threads = threading.Thread()     # Worker threads
 - each thread:
	 more_requests = True
	 pending_request_queue = deque()
	 loop until more_requests==False and pending_request_queue is empty:
	   if more_requests:
		 with request_lock:
			try:
				request = request_iter.next()
			except StopIteration:
				more_requests = False
				continue
			request_buffer = request_buffer + (fmt % request) + "\n"
			pending_request_queue.append(request)
		 etc...

Constraints:
 - the "requests" iterator is invoked serially from different threads,
   so lists and simple generators work okay, but fancy stuff may not.
 - the order in which answers come back is not deterministic
"""

def query_blocks(requests, fmt, parse_fn, thread_count = 20):
	def worker_fn(mc_socket, request_iter, request_lock, answer_queue,):
		more_requests = True
		request_buffer = bytes()
		response_buffer = bytes()
		pending_request_queue = collections.deque()
		while more_requests or len(pending_request_queue) > 0:
			# Grab more requests
			while more_requests and len(request_buffer) < 4096:
				with request_lock:
					try:
						request = next(request_iter)
					except StopIteration:
						more_requests = False
						continue
					new_request_str = (fmt % request) + "\n"
					request_buffer = request_buffer + new_request_str.encode('utf-8')
					# request_buffer = request_buffer + (fmt % request) + "\n"
					pending_request_queue.append(request)

			# Select I/0 we can perform without blocking
			w = [mc_socket] if len(request_buffer) > 0 else []
			r, w, x = select.select([mc_socket], w, [], 5)
			allow_read = bool(r)
			allow_write = bool(w)

			# Write requests to the server
			if allow_write:
				# Write exactly once
				bytes_written = mc_socket.send(request_buffer)
				request_buffer = request_buffer[bytes_written:]
				if bytes_written == 0:
					raise RuntimeError("unexpected socket.send()=0")

			# Read responses from the server
			if allow_read:
				# Read exactly once
				bytes_read = mc_socket.recv(1024)
				response_buffer = response_buffer + bytes_read
				if bytes_read == 0:
					raise RuntimeError("unexpected socket.recv()=0")

			# Parse the response strings
			responses = response_buffer.split('\n'.encode('utf-8'))
			response_buffer = responses[-1]
			responses = responses[:-1]
			for response_string in responses:
				request = pending_request_queue.popleft()
				answer_queue.put((request, parse_fn(response_string)))

	request_lock = threading.Lock() # to serialize workers getting
									# the next request
	answer_queue = queue.Queue()  # To store answers coming back from
								  # the worker threads
	sockets = []
	try:
		for i in range(thread_count):
			sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
			sockets[-1].connect(("localhost", 4711))
		workers = []
		threading.stack_size(128 * 1024)  # bytes
		for w in range(thread_count):
			t = threading.Thread(target = worker_fn,
								 args = (sockets[w],
										 iter(requests),
										 request_lock,
										 answer_queue))
			t.start()
			workers.append(t)
			
		# Wait for workers to finish
		for w in workers:
			w.join()
	except socket.error as e:
		print("Socket error:", e)
		print("Is the Minecraft server running?")
		raise e
	finally:
		for s in sockets:
			try:
				s.shutdown(socket.SHUT_RDWR)
				s.close()
			except socket.error as e:
				pass
	
	# Collect results
	while not answer_queue.empty():
		yield answer_queue.get()

def parse_to_block(ans):
	return Block(*map(int, ans.decode("utf-8").split(",")))

def parse_to_tuple(ans):
	return tuple(map(int, ans.decode("utf-8").split(",")))

if __name__ == "__main__":
	pass