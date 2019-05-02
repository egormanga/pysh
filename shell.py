#!/usr/bin/python3
# PySH Shell

from . import env
from utils.nolog import *

class Command(abc.ABC):
	def __init__(self, cmd, *args):
		self.cmd, self.args = cmd, args
		self.stdin = sys.stdin
		self.stdout = sys.stdout
		self.stderr = sys.stderr

	@abc.abstractmethod
	def run(self):
		pass

	def wait(self):
		pass

	def getoutput(self):
		self.stdout = io.StringIO()
		self.run()
		self.wait()
		return self.stdout.getvalue()

	def complete(self, text):
		pass

class BuiltinCommand(Command): pass

class NativeCommand(Command):
	def run(self):
		self.process = subprocess.Popen((self.cmd, *self.args), executable=shutil.which(self.cmd), stdin=self.stdin, stdout=self.stdout, stderr=self.stderr, universal_newlines=True)
		self.wait = self.process.wait

	def getoutput(self):
		self.run()
		return self.process.communicate()[0]

class PythonCommand(Command):
	def run(self):
		try: r = eval(self.cmd, globals())
		except BaseException as ex:
			self.stderr.write(f"\033[91m{type(ex).__name__}\033[0m{f': {ex}' if (str(ex)) else ''}\n")
			env.lastex = sys.exc_info()
		else:
			if (r is not None): self.stdout.write(repr(r)+'\n')

class cd(BuiltinCommand):
	def run(self):
		os.chdir(self.args[0] if (self.args) else os.environ['HOME'])

class tb(BuiltinCommand):
	def run(self):
		self.stderr.write(traceback.format_exception(*env.lastex))

class which(BuiltinCommand):
	def run(self):
		if (len(self.args) < 1): return
		self.stdout.write(shutil.which(self.args[0])+'\n')

class clear(BuiltinCommand):
	def run(self):
		sys.stderr.write('\033c')

class exit(BuiltinCommand):
	def run(self):
		sys.exit()

builtin_commands = {i.__name__: i for i in BuiltinCommand.__subclasses__()}

# by Sdore, 2019
