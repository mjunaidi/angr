import simuvex # pylint: disable=F0401
import copy

max_fds = 8192

class SimStateSystem(simuvex.SimStatePlugin):
	def __init__(self, initialize=True, files=None):
		simuvex.SimStatePlugin.__init__(self)
		self.maximum_symbolic_syscalls = 255
		self.files = { } if files is None else files
		self.max_length = 2 ** 16

		if initialize:
			self.open("stdin", "r") # stdin
			self.open("stdout", "w") # stdout
			self.open("stderr", "w") # stderr

	def open(self, name, mode):
		# TODO: speed this up
		for fd in xrange(0, 8192):
			if fd not in self.files:
				self.files[fd] = simuvex.SimFile(fd, name, mode)
				return fd

	@simuvex.helpers.concretize_args
	def read(self, fd, length):
		# TODO: error handling
		# TODO: symbolic support
		expr, constraints = self.files[fd].read(length)
		self.state.add_constraints(*constraints)
		return expr

	@simuvex.helpers.concretize_args
	def write(self, fd, content, length):
		# TODO: error handling
		# TODO: symbolic support
		return self.files[fd].write(content, length)

	@simuvex.helpers.concretize_args
	def close(self, fd):
		# TODO: error handling
		# TODO: symbolic support?
		del self.files[fd]

	@simuvex.helpers.concretize_args
	def seek(self, fd, seek):
		# TODO: symbolic support?
		self.files[fd].seek(seek)

	def copy(self):
		files = { fd:f.copy() for fd,f in self.files.iteritems() }
		return SimStateSystem(False, files)

	def merge(self, other, merge_flag, flag_us_value):
		if self.files.keys() != other.files.keys():
			raise simuvex.SimMergeError("Unable to merge SimStateSystem with different sets of open files.")

		for fd in self.files:
			self.files[fd].merge(other.files[fd], merge_flag, flag_us_value)

simuvex.SimStatePlugin.register_default('posix', SimStateSystem)
