import options
import random

SUBCHUNK_WIDTH  = 4
SUBCHUNK_HEIGHT = 4
SUBCHUNK_LENGTH = 4

class Subchunk:
	def __init__(self, parent, subchunk_position):
		self.parent = parent
		self.world = self.parent.world

		self.subchunk_position = subchunk_position

		self.local_position = (
			self.subchunk_position[0] * SUBCHUNK_WIDTH,
			self.subchunk_position[1] * SUBCHUNK_HEIGHT,
			self.subchunk_position[2] * SUBCHUNK_LENGTH)

		self.position = (
			self.parent.position[0] + self.local_position[0],
			self.parent.position[1] + self.local_position[1],
			self.parent.position[2] + self.local_position[2])

		# mesh variables

		self.mesh = []
		self.translucent_mesh = []
	
	def add_face(self, face, pos, block_type):
		rotation = 0
		if options.ALTERNATE_BLOCKS and block_type.is_cube and not block_type.transparent:
			rotation = random.randint(0, 3)
		x, y, z = pos
		vertex_positions = block_type.vertex_positions[face]
		tex_index = block_type.tex_indices[face]
		shading_values = block_type.shading_values[face]

		if block_type.model.translucent:
			mesh = self.translucent_mesh
		else:
			mesh = self.mesh
		
		for i in range(4):
			mesh.append(vertex_positions[i * 3 + 0] + x)
			mesh.append(vertex_positions[i * 3 + 1] + y)
			mesh.append(vertex_positions[i * 3 + 2] + z)

			mesh.append((i + rotation) % 4)
			mesh.append(tex_index)

			mesh.append(shading_values[i])

	def can_render_face(self, block_type, block_number, position):
		return not (self.world.is_opaque_block(position)
			or (block_type.glass and self.world.get_block_number(position) == block_number)) \
			or (block_type.translucent and self.world.get_block_number(position) != block_number)
			

	def update_mesh(self):
		self.mesh = []
		self.translucent_mesh = []

		for local_x in range(SUBCHUNK_WIDTH):
			for local_y in range(SUBCHUNK_HEIGHT):
				for local_z in range(SUBCHUNK_LENGTH):
					parent_lx = self.local_position[0] + local_x
					parent_ly = self.local_position[1] + local_y
					parent_lz = self.local_position[2] + local_z

					block_number = self.parent.blocks[parent_lx][parent_ly][parent_lz]

					if block_number:
						block_type = self.world.block_types[block_number]

						x, y, z = pos = (
							self.position[0] + local_x,
							self.position[1] + local_y,
							self.position[2] + local_z)
						

						# if block is cube, we want it to check neighbouring blocks so that we don't uselessly render faces
						# if block isn't a cube, we just want to render all faces, regardless of neighbouring blocks
						# since the vast majority of blocks are probably anyway going to be cubes, this won't impact performance all that much; the amount of useless faces drawn is going to be minimal

						if block_type.is_cube:
							if self.can_render_face(block_type, block_number, (x + 1, y, z)): self.add_face(0, pos, block_type)
							if self.can_render_face(block_type, block_number, (x - 1, y, z)): self.add_face(1, pos, block_type)
							if self.can_render_face(block_type, block_number, (x, y + 1, z)): self.add_face(2, pos, block_type)
							if self.can_render_face(block_type, block_number, (x, y - 1, z)): self.add_face(3, pos, block_type)
							if self.can_render_face(block_type, block_number, (x, y, z + 1)): self.add_face(4, pos, block_type)
							if self.can_render_face(block_type, block_number, (x, y, z - 1)): self.add_face(5, pos, block_type)
						
						else:
							for i in range(len(block_type.vertex_positions)):
								self.add_face(i, pos, block_type)
