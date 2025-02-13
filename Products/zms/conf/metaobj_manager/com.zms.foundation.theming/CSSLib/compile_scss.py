##  Using pyScss

def compile_scss(self, scss=''):
	""" 
	Please make sure that https://pypi.org/project/pyScss/ is installed 
	"""
	try:
		from scss import Compiler
		css = Compiler().compile_string(scss)
	except:
		css = '/* COMPILER ERROR: Details see Zope event.log */'

	# clean whitespace
	css_lines = [ l.lstrip() for l in css.split('\n') ]
	return '\n'.join(css_lines)