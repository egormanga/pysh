#!/usr/bin/python3
# PySH

import git, PyT9, readline, rlcompleter
from . import env, shell
from utils.nolog import *

histfile = os.path.expanduser('~/.pysh_history')

def prompt():
	sep = '\ue0b0'
	branch = '\ue0a0'
	p = (
		(96, 30),
		(39, 34),
		(90, 92),
	)

	r = list()
	li = int()
	for ii, i in enumerate((
		'@'.join((os.environ['USER'], socket.gethostname())),
		re.sub(rf"^{os.environ['HOME']}", '~', os.path.realpath(os.path.curdir)),
		' '.join((branch, git.Repo().head.ref.name)) if (os.path.isdir('.git')) else '',
	)):
		if (not i): continue
		r.append(f"\1\033[{p[ii-1][1]};{p[ii][1]+10}m\2{sep if (ii) else ''}\1\033[{p[ii][0]}m\2 {i}")
		li = ii
	r.append(f"\1\033[0;{p[li][1]}m\2{sep}\1\033[0m\2 ")
	return ' '.join(r)

def readexpr(c=''):
	try: c += input('... ' if (c) else prompt())
	except EOFError:
		if (c): sys.stderr.write('\r\033[K'); return
		exit()
	return expr(c)

def expr(c):
	# TODO: proper expansion and other processing
	c = re.sub(r'(?<!\\)`(.*?)(?<!\\)`', lambda x: ' '.join(expr(x[1]).getoutput().split()), c) # FIXME wrong pattern 🤔️
	if (c[:3] in ('sh:', 'py:')): mode, _, c = c.partition(':')
	else: mode = None
	c = c.strip()
	sc = re.split(r'(?<!\\) ', c)

	if (mode != 'py'):
		if (sc[0] in shell.builtin_commands): return shell.builtin_commands[sc[0]](*sc)
		if (shutil.which(sc[0])): return shell.NativeCommand(*sc)
	if (mode == 'sh'): print(f"Command not found: «{sc[0]}»"); return

	try: return shell.PythonCommand(compile(c, '<pysh>', 'eval'))
	except SyntaxError:
		try: return shell.PythonCommand(compile(c, '<pysh>', 'exec'))
		except SyntaxError as ex:
			if ('unexpected EOF while parsing' in ex.args[0]): return readexpr(c+'\n')

class Completer(rlcompleter.Completer):
	def global_matches(self, text):
		return super().global_matches(text) + glob.glob(text+'*')
completer = Completer()

_exit = exit
def exit(*args, **kwargs):
	parseargs(kwargs, nolog=True)
	_exit(*args, **kwargs)

def main():
	try: readline.read_history_file(histfile)
	except FileNotFoundError: pass
	for i in (
		#'set blink-matching-paren on',
		'set colored-completion-prefix on',
		#'set colored-stats on',
		'set enable-bracketed-paste on',
		#'set horizontal-scroll-mode on',
		'set skip-completed-text on',
		'tab: complete',
	): readline.parse_and_bind(i)
	readline.set_completer(completer.complete)
	readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?') # TODO
	#readline.set_completion_display_matches_hook(completer.display) # also TODO

	try:
		while (True):
			try:
				p = readexpr()
				if (p is None): continue
				p.run()
				p.wait()
			except KeyboardInterrupt as ex: print(f"\033[2m^C\n{type(ex).__name__}\033[0m")
	finally: readline.write_history_file(histfile)

if (__name__ == '__main__'): exit(main())

# by Sdore, 2019
