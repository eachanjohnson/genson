#!/usr/bin/env python

"""This script takes markdown files in the specified directory as input (MUST have 
extension .md) and converts them to HTML. The new HTML file will be in a directory tree 
according to year and month, and the filename will be based on the title of the page.

Optionally, the generated HTML code will be inserted into another HTML template. Also 
optionally, an HTML link contents pages will be generated, also inserted into a 
template."""

# Import things we need
import argparse		# For getting command line arguments
import markdown		# For interpreting markdown files
import time 		# For timestamps and such
import os			# For getting file metadata
import subprocess	# For issuing bash commands
import string 		# To get alphabet
import sys			# For quitting on error
letters = string.letters + ' ' 
try:
	import cStringIO # For making HTML buffers before writing
except:
	import StringIO
	
# Define functions
def get_md_files(directory):
	"""
	Get markdown files in a given directory.
	"""
	bash_command = ['ls', '-1', '{}'.format(directory)] # Get one-per-line output
	try:
		input_dir_files = subprocess.check_output(bash_command).split('\n')
	except subprocess.CalledProcessError:
		sys.exit("No Markdown files in this directory: {}".format(args.input_dir))
	else:
		# Get only Markdown files
		md_files = [file for file in input_dir_files if file[-3:] == '.md'] 
		return md_files
		
def prepare_template(template):
	"""
	Alter the template file.
	"""
	# If there is a template provided, store head and tail for later
	d = {'total': '', 'head': '', 'tail': ''}
	try:
		with open('{}.html'.format(template), 'rU') as f:
			d['total'] = f.read()
	except:
		sys.exit('The template file {}.html doesn\'t exist.'.format(template))
	else:
		d['total'] = \
			d['total'].replace('CSS_FILE','../../../../../{}.css'.format(template))
		d['total'] = \
			d['total'].replace('JS_FILE','../../../../../{}.js'.format(template))
		d['head'] = d['total'].split('INSERT_POST_HERE')[0]
		d['tail'] = d['total'].split('INSERT_POST_HERE')[1]
		return d
		
def get_file_info(filename):
	"""
	Get file metadata as a dictionary.
	"""
	d = {'date': {}, 'time': {}}
	modtime = time.gmtime(os.path.getmtime(input_file))
	createtime = time.gmtime(os.path.getctime(input_file))
	d['date']['modified'] = \
		time.strftime('%Y,%m,%d', modtime).split(',')
	d['time']['modified'] = \
		time.strftime('%I,%M,%p', modtime).split(',')
	d['date']['created'] = \
		time.strftime('%Y,%m,%d', createtime).split(',')
	d['time']['created'] = \
		time.strftime('%I,%M,%p', createtime).split(',')
	return d
	
def md2html(parser, filename, template):
	"""
	Convert markdown file to dict of HTML string and file title.
	"""
	o = {'title': '', 'html': ''}
	# Start a new cache
	cache = cStringIO.StringIO()
	# Start with template head
	cache.write('{}'.format(template['head']))
	# Loop through the lines, coverting to HTML as we go
	with open(filename, 'rU') as f:
		for n, line in enumerate(f):
			cache.write('{}'.format(parser.convert(line)))
			parser.reset()
			if n != 0:
				pass
			else:
				# If on title line, use it to create URL slug
				title_slug = line.rstrip()
				title_slug = [letter.lower() for letter in title_slug if letter in letters]
				title_slug = ''.join(title_slug)
				title_slug = title_slug.split(' ')
				title_slug = '-'.join([word for word in title_slug if word != ''])
	# Add tail to cache
	cache.write('{}'.format(template['tail']))
	o['title'] = title_slug
	o['html'] = cache.getvalue()
	return o
	
def html_out(htmldict, outdir, info):
	"""
	Writes HTML out into a directory tree.
	"""
	# Make output directory
	output_dir = '{}/{}/{}/{}/{}'.format(
		outdir, 
		info['date']['created'][0], 
		info['date']['created'][1], 
		info['date']['created'][2], 
		htmldict['title']
	)
	try:
		os.makedirs(output_dir)
	except OSError:
		print '{}/ already exists'.format(output_dir)
	# Construct output filename
	output_file = '{}/index.html'.format(output_dir)
	# Write cache to HTML file
	with open(output_file, 'w') as f:
		f.write('{}'.format(html['html']))
		print 'Wrote: {}'.format(output_file)
	return output_file
	


# Initialize argparse
parser = argparse.ArgumentParser(
	description="""
This script takes markdown files in the specified directory as input (MUST have 
extension .md) and converts them to HTML. The new HTML file will be in a directory tree 
according to year and month, and the filename will be based on the title of the page.

Optionally, the generated HTML code will be inserted into another HTML template. Also 
optionally, an HTML link contents pages will be generated, also inserted into a 
template.
"""
	)	
# Add arguments
parser.add_argument(
	'-i',
	action='store',
	nargs='?',
	default='.',
	type=str,
	required=False,
	help='Directory containing the Markdown files to be converted.',
	dest='input_dir'
)
parser.add_argument(
	'-o',
	action='store',
	nargs='?',
	default='blog',
	type=str,
	required=False,
	help='Destination directory for contructing the output tree.',
	dest='output_dir'
)
parser.add_argument(
	'-t',
	action='store',
	nargs='?',
	type=str,
	required=False,
	help='Name of the HTML/CSS/JS templates to be used to generate static pages.',
	dest='template'
)
parser.add_argument(
	'-c',
	action='store',
	nargs='?',
	default=False,
	type=bool,
	required=False,
	choices=[True, False],
	help='Should a table of contents be generated?',
	dest='create_toc'
)
args = parser.parse_args()

# Get all markdown files in input directory
md_files = get_md_files(directory=args.input_dir)

# If there is a template, use it
if args.template:
	template = prepare_template(template=args.template)
else:
	template = {'total': '', 'head': '', 'tail': ''}

# Initialize the Markdown parser
md_parser = markdown.Markdown()

# Go through the MD files and convert to HTML
for md in md_files:
	input_file = '{}/{}'.format(args.input_dir, md)
	# Get info about this particular input file
	file_info = get_file_info(filename=input_file)
	# Convert to HTML
	html = md2html(parser=md_parser, filename=input_file, template=template)
	# Write to a new file
	new_file = html_out(htmldict=html, outdir=args.output_dir, info=file_info)
				
quit()