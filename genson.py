#!/usr/bin/env python

# This script takes markdown files in the specified directory as input (MUST have 
# extension .md) and converts them to HTML. The new HTML file will be in a directory tree 
# according to year and month, and the filename will be based on the title of the page.
# 
# Optionally, the generated HTML code will be inserted into another HTML template. Also 
# optionally, an HTML link contents pages will be generated, also inserted into a 
# template.

# Import things we need
import argparse		# For getting command line arguments
import markdown		# For interpreting markdown files
import time 		# For timestamps and such
import os			# For getting file metadata
import subprocess	# For issuing bash commands
import string 		# To get alphabet
letters = string.letters + ' ' 
try:
	import cStringIO # For making HTML buffers before writing
except:
	import StringIO

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
	default='blog_template',
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
bash_command = ['ls', '-1', '{}'.format(args.input_dir)] # Get one-per-line output
try:
	input_dir_files = subprocess.check_output(bash_command).split('\n')
except subprocess.CalledProcessError:
	sys.exit("No Markdown files in this directory: {}".format(args.input_dir))

# Get only Markdown files
md_files = [file for file in input_dir_files if file[-3:] == '.md'] 

# Initialize the Markdown parser
md_parser = markdown.Markdown()

# Go through the MD files and convert to HTML
for md in md_files:
	# Make an empty cache which will eventually be written to HTML
	cache = cStringIO.StringIO()
	
	# Get info about this particular input file
	input_file = '{}/{}'.format(args.input_dir, md)
	date_modified = \
		time.strftime('%Y,%m,%d', time.gmtime(os.path.getmtime(input_file))).split(',')
	time_modified = \
		time.strftime('%I,%M,%p', time.gmtime(os.path.getmtime(input_file))).split(',')
	date_created = \
		time.strftime('%Y,%m,%d', time.gmtime(os.path.getctime(input_file))).split(',')
	time_created = \
		time.strftime('%I,%M,%p', time.gmtime(os.path.getctime(input_file))).split(',')
	
	# Loop through the lines, coverting to HTML as we go
	with open(input_file, 'rU') as f:
		for n, line in enumerate(f):
			cache.write('{}'.format(md_parser.convert(line)))
			md_parser.reset()
			if n != 0:
				pass
			else:
				title_slug = line.rstrip()
				title_slug = [letter.lower() for letter in title_slug if letter in letters]
				title_slug = ''.join(title_slug)
				title_slug = title_slug.split(' ')
				title_slug = '-'.join(title_slug)
	
	# Make output directory
	output_dir = '{}/{}/{}/{}'.format(
		args.output_dir, date_created[0], date_created[1], date_created[2]
	)
	try:
		os.makedirs(output_dir)
	except OSError:
		print '{} already exists'.format(output_dir)
	
	# Construct output filename
	output_file = '{}/{}.html'.format(output_dir, title_slug)
	print output_file
	
	# Write cache to HTML file
	with open(output_file, 'w') as f:
		f.write('{}'.format(cache.getvalue()))
			
quit()