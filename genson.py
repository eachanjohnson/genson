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
	d = {'title': '', 'slug': '', 'html': '', 'md_content': ''}
	# Start a new cache
	cache = cStringIO.StringIO()
	# Loop through the lines, coverting to HTML as we go
	with open(filename, 'rU') as f:
		for n, line in enumerate(f):
			cache.write('{}'.format(parser.convert(line)))
			parser.reset()
			if n != 0:
				pass
			else:
				# If on title line, use it to create URL slug
				title = [letter for letter in line.rstrip() if letter in letters]
				slug = ''.join([letter.lower() for letter in title])
				title = ''.join(title)
				slug = slug.split(' ')
				slug = '-'.join([word for word in slug if word != ''])
	d['md_content'] = cache.getvalue()
	d['title'] = title
	d['slug'] = slug
	d['html'] = '{}{}{}'.format(template['head'], d['md_content'], template['tail'])
	cache.close()
	return d
	
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
		htmldict['slug']
	)
	try:
		os.makedirs(output_dir)
	except OSError:
		print '{}/ already exists'.format(output_dir)
	# Construct output filename
	output_file = '{}/index.html'.format(output_dir)
	# Write cache to HTML file
	with open(output_file, 'w') as f:
		f.write('{}'.format(htmldict['html']))
		print 'Wrote: {}'.format(output_file)
	return output_file

def toc_update(toc, new, htmldict):
	"""
	Adds blog post from filename to a dictionary for making front page and ToC.
	"""
	d = {}
	new_meta = new.split('index.html')[0].split('/')
	preview = '{}<strong>...</strong>'.format(htmldict['md_content'][:1000])
	new_post = {'path': new, 'preview': preview, 'title': htmldict['title']}
	try:
		d[new_meta[1]][new_meta[2]][new_meta[3]][new_meta[4]] = new_post
	except KeyError:
		try:
			d[new_meta[1]][new_meta[2]][new_meta[3]] = {new_meta[4]: new_post}
		except KeyError:
			try:
				d[new_meta[1]][new_meta[2]] = {
					new_meta[3]: {new_meta[4]: new_post}
				}
			except KeyError:
				d[new_meta[1]] = {
					new_meta[2]: {
						new_meta[3]: {new_meta[4]: new_post}
					}
				}
	return d
	
def toc2html(template, toc):
	"""
	Converts ToC dict to html, then inserts into template.
	"""
	# Make new cache
	cache = cStringIO.StringIO()
	# Get list of years, reverse it
	years = sorted(toc)
	years.reverse()
	for year in years:
		cache.write('<h2>{}</h2>\n'.format(year))
		months = sorted(toc[year])
		months.reverse()
		for month in months:
			cache.write('<h3>{}</h3>\n'.format(month))
			days = sorted(toc[year][month])
			days.reverse()
			for day in days:
				cache.write('<h4>{}</h4>\n<ul>\n'.format(day))
				posts = toc[year][month][day]
				for post in posts:
					href = toc[year][month][day][post]['path'].split('/')[1:]
					href = '/'.join([dir for dir in href if dir != ''])
					title = toc[year][month][day][post]['title']
					cache.write('<li><a href="{}" class="contents-item">{}</a></li>\n'.format(href, title))
				cache.write('\n</ul>\n'.format(year))
	html_toc = cache.getvalue()
	cache.close()
	s = '{}<br><h1>Table of Contents</h1><br><br>\n{}{}'.format(
		template['head'], 
		html_toc, 
		template['tail']
	)
	return s
	
def toc_out(htmlstr, outdir, filename):
	"""
	Writes out table of contents or front page
	"""
	# Construct output filename
	output_file = '{}/{}.html'.format(outdir, filename)
	# Write cache to HTML file
	with open(output_file, 'w') as f:
		f.write('{}'.format(htmlstr))
		print 'Wrote: {}'.format(output_file)
	return output_file
	
def toc2fp(template, toc):
	"""
	Converts ToC dict to html for front page, then inserts into template.
	"""
	# Make new cache
	cache = cStringIO.StringIO()
	# Get list of years, reverse it
	years = sorted(toc)
	years.reverse()
	for year in years:
		months = sorted(toc[year])
		months.reverse()
		for month in months:
			days = sorted(toc[year][month])
			days.reverse()
			for day in days:
				posts = toc[year][month][day]
				for post in posts:
					href = toc[year][month][day][post]['path'].split('/')[1:]
					href = '/'.join([dir for dir in href if dir != ''])
					preview = toc[year][month][day][post]['preview']
					cache.write('{}\n'.format(preview))
	html_toc = cache.getvalue()
	cache.close()
	s = '{}{}{}'.format(
		template['head'], 
		html_toc, 
		template['tail']
	)
	return s

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

# Initialize dict of new posts
toc = {}

# Go through the MD files and convert to HTML
for md in md_files:
	input_file = '{}/{}'.format(args.input_dir, md)
	# Get info about this particular input file
	file_info = get_file_info(filename=input_file)
	# Convert to HTML
	html = md2html(parser=md_parser, filename=input_file, template=template)
	# Write to a new file
	new_file = html_out(htmldict=html, outdir=args.output_dir, info=file_info)
	# Update dictionary of new posts
	toc = toc_update(toc=toc, new=new_file, htmldict=html)
	
# Add a table of contents in the blog root
html_toc = toc2html(template=template, toc=toc)
toc_file = toc_out(htmlstr=html_toc, outdir=args.output_dir, filename='toc')

# Make a front page in the blog root
html_fp = toc2fp(template=template, toc=toc)
fp_file = toc_out(htmlstr=html_fp, outdir=args.output_dir, filename='index')
			
quit()