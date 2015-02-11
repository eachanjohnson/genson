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
	
# Define objects
class MarkdownFiles(object):
	"""
	Represents the markdown files in a directory.
	"""
	def __init__(self, directory):
		self.source_dir = directory
		self.filenames = self.get_filenames()
		
	def get_filenames(self):
		"""
		Get markdown files in a given directory.
		"""
		bash_command = ['ls', '-1', '{}'.format(self.source_dir)] # Get one-per-line output
		try:
			input_dir_files = subprocess.check_output(bash_command).split('\n')
		except subprocess.CalledProcessError:
			sys.exit("!!! Error in directory. Is this correct?: {}".format(self.source_dir))
			return None
		else:
			# Get only Markdown files
			md_files = [f for f in input_dir_files if f[-3:] == '.md']
			if len(md_files) > 0: 
				return md_files
			else:
				sys.exit("!!! Warning: No Markdown files in this directory: \
					{}".format(self.source_dir))
				return None
		

class Template(object):
	"""
	Represents the template into which will be inserted the post and any modifications.
	"""
	def __init__(self, directory):
		self.source_dir = directory
		self.html_file = self.get_html_filename()
		self.source_html = open('{}/{}'.format(self.source_dir, self.html_file), 'rU').read()
		self.path_back_templates = './{}/'.format(self.source_dir)
		self.path_back_root = './{}/'.format(self.source_dir)
		self.path_back_other = './{}/'.format(self.source_dir)
		self.html = self.update_html()
		
	def get_html_filename(self):
		"""
		"""
		bash_command = ['ls', '-1', '{}'.format(self.source_dir)] # Get one-per-line output
		try:
			input_dir_files = subprocess.check_output(bash_command).split('\n')
		except subprocess.CalledProcessError:
			sys.exit("Warning: No files in template directory. \
				Is this correct?: {}/".format(self.source_dir))
			return None
		else:
			# Get only HTML files
			html_files = [f for f in input_dir_files if f[-5:] == '.html']
			if len(html_files) > 0: 
				if len(html_files) != 1:
					sys.exit("!!! Warning: More than one HTML file in template directory. \
						Is this correct?: {}/".format(', '.join(html_files)))
				else:
					return html_files[0]	
			else:
				sys.exit("!!! Warning: No HTML files in this directory. \
					Is this correct?: {}/".format(self.source_dir))
				return None
		
	def find_path_back_templates(self, currentdir):
		"""
		"""
		relative_path = ''
		target_path = self.source_dir.split('/')
		start_path = currentdir.split('/')
		while len(start_path) > 1 and target_path != start_path:
			start_path.pop()
			relative_path += '../'
		relative_path += '../' + '/'.join(target_path) + '/'
		self.path_back_templates = relative_path
		return relative_path
		
	def find_path_back_root(self, currentdir):
		"""
		"""
		relative_path = ''
		target_path = ['']
		start_path = currentdir.split('/')
		while len(start_path) > 2 and target_path != start_path:
			start_path.pop()
			relative_path += '../'
		relative_path += '../' + '/'.join(target_path) + '/'
		self.path_back_root = relative_path
		return relative_path
		
	def find_path_back_other(self, path):
		"""
		"""
		relative_path = path
		self.path_back_root = relative_path
		return relative_path
		
	def update_html(self):
		"""
		"""
		source = self.source_html
		self.html = source.replace('//genson.path//', '{}'.format(self.path_back_templates))
		self.html = self.html.replace('//genson.return//', '{}'.format(self.path_back_root))
		return self.html
		
		
class BlogPost(object):
	"""
	Represents an individual blog post.
	"""
	def __init__(self, markdown, rootdir, parser, template):
		self.sourcefile = markdown
		self.timestamp = self.get_time()
		self.root_path = rootdir
		self.md = open(markdown, 'rU').read()
		self.preview = self.get_preview()
		self.title = self.get_title()
		self.slug = self.get_slug()
		self.path = self.make_path()
		self.parser = parser
		self.preview_html = self.converter('.genson-preview.temp', 'preview')
		self.post_html = self.converter(self.sourcefile, 'blog-post')
		self.template = template
		self.html = self.construct_page(self.template)
		self.outputfile = self.write_out()
		subprocess.call(['rm', '.genson-preview.temp'])
		
	def get_time(self):
		"""
		Get file metadata as a dictionary.
		"""
		d = {'date': {}, 'time': {}}
		modtime = time.gmtime(os.path.getmtime(self.sourcefile))
		createtime = time.gmtime(os.path.getctime(self.sourcefile))
		d['date']['modified'] = \
			time.strftime('%Y,%m,%d', modtime).split(',')
		d['time']['modified'] = \
			time.strftime('%I,%M,%p', modtime).split(',')
		d['date']['created'] = \
			time.strftime('%Y,%m,%d', createtime).split(',')
		d['time']['created'] = \
			time.strftime('%I,%M,%p', createtime).split(',')
		return d
			
	def make_path(self):
		"""
		"""
		# Make output directory
		output_dir = '{}/{}/{}/{}/{}'.format(
			self.root_path, 
			self.timestamp['date']['created'][0], 
			self.timestamp['date']['created'][1], 
			self.timestamp['date']['created'][2], 
			self.slug
		)
		try:
			os.makedirs(output_dir)
		except OSError:
			print '{} already exists'.format(output_dir)
		return output_dir
		
	def get_preview(self):
		"""
		"""
		cache = cStringIO.StringIO()
		with open(self.sourcefile, 'rU') as f:
			in_preview = False
			for line in f:
				if '//genson.startpreview//' in line:
					in_preview = True
				elif '//genson.endpreview//' in line:
					in_preview = False
				else:
					if in_preview:
						cache.write('{}'.format(line))
					else:
						pass
		s = cache.getvalue()
		cache.close()
		with open('.genson-preview.temp', 'w') as f:
			f.write(s)
		return s
		
	def converter(self, markdown, mode):
		"""
		"""
		cache = cStringIO.StringIO()
		cache.write('<div class="{}">'.format(mode))
		# Loop through the lines, coverting to HTML as we go
		with open(markdown, 'rU') as f:
			for n, line in enumerate(f):
				try:
					cache.write('{}'.format(self.parser.convert(line)))
				except UnicodeDecodeError as e:
					sys.exit(
						'\nError parsing Markdown on line {}:\n{}\n{}'.format(n, line, e)
					)
				else:
					self.parser.reset()					
		cache.write('</div>')
		s = cache.getvalue()
		cache.close()
		s = s.replace('//genson.startpreview//', '')
		s = s.replace('//genson.endpreview//', '')
		s = s.replace(
			'//genson.created//', 
			'<span class="byline">\n{}-{}-{} at {}:{} {}\n</span>'.format(
			self.timestamp['date']['created'][2],
			self.timestamp['date']['created'][1],
			self.timestamp['date']['created'][0],
			self.timestamp['time']['created'][0],
			self.timestamp['time']['created'][1],
			self.timestamp['time']['created'][2]
		))
		s = s.replace(
			'//genson.modified//', 
			'<span class="byline">\n{}-{}-{} at {}:{} {}\n</span>'.format(
			self.timestamp['date']['modified'][2],
			self.timestamp['date']['modified'][1],
			self.timestamp['date']['modified'][0],
			self.timestamp['time']['modified'][0],
			self.timestamp['time']['modified'][1],
			self.timestamp['time']['modified'][2]
		))
		return s
		
	def construct_page(self, template):
		"""
		"""
		# Get template
		template.find_path_back_templates(self.path)
		template.find_path_back_root(self.path)
		template.update_html()
		t = template.html
		# Insert post html
		page = t.replace('//genson.insertpost//', self.post_html)
		page = page.replace('//genson.title//', self.title)
		return page
	
	def get_title(self):
		"""
		"""
		title = ''
		with open(self.sourcefile, 'rU') as f:
			for n, line in enumerate(f):
				if n == 0:
					# If on title line, use it to create URL slug
					title = [letter for letter in line.rstrip() if letter in letters]
					title = ''.join(title)
					break
				else:
					pass		
		return title
		
	def get_slug(self):
		"""
		"""
		slug = ''.join([letter.lower() for letter in self.title])
		slug = slug.split(' ')
		slug = '-'.join([word for word in slug if word != ''])
		return slug
		
	def write_out(self):
		"""
		"""
		filename = '{}/index.html'.format(self.path)
		with open(filename, 'w') as f:
			f.write('{}'.format(self.html))
			print('Wrote blog post: {}'.format(filename))
		return filename
		

class TableOfContents(object):
	"""
	Represents a table of contents data structure. Constructs from a list of blog posts.
	"""
	def __init__(self, posts, rootdir, template):
		self.root = rootdir
		self.post_list = posts
		self.template = template
		self.time_toc = self.generate_time_toc()
		self.time_toc_html = self.generate_time_toc_html()
		self.fp_html = self.generate_fp_html()
		#self.index = self.generate_search_index()
		self.html = self.construct_page(self.fp_html, self.template)
		self.outputfile = self.write_out()
		
	def generate_time_toc(self):
		"""
		"""
		toc = {}
		for post in self.post_list:
			y = post.timestamp['date']['created'][2]
			m = post.timestamp['date']['created'][1]
			d = post.timestamp['date']['created'][0]
			try:
				toc[y][m][d].append(post)
			except KeyError:
				try:
					toc[y][m] = {
						d: [post]
					}
				except KeyError:
					toc[y] = {
						m: {
							d: [post]
						}
					}
		return toc
		
	def generate_time_toc_html(self):
		"""
		"""
		# Make new cache
		cache = cStringIO.StringIO()
		# Get list of years, reverse it
		years = sorted(self.time_toc)
		years.reverse()
		for year in years:
			cache.write('<h2>{}</h2>\n'.format(year))
			months = sorted(self.time_toc[year])
			months.reverse()
			for month in months:
				cache.write('<h3>{}</h3>\n'.format(month))
				days = sorted(self.time_toc[year][month])
				days.reverse()
				for day in days:
					cache.write('<h4>{}</h4>\n<ul>\n'.format(day))
					posts = self.time_toc[year][month][day]
					for post in posts:
						href = post.path.split('/')[1:]
						href = '/'.join([dir for dir in href if dir != ''])
						title = post.title
						cache.write('<li><a href="{}" class="contents-item">{}</a></li>\n'.format(href, title))
					cache.write('\n</ul>\n'.format(year))
		s = cache.getvalue()
		cache.close()
		return s
	
	def generate_fp_html(self):
		"""
		Converts ToC dict to html for front page, then inserts into template.
		"""
		# Make new cache
		cache = cStringIO.StringIO()
		# Get list of years, reverse it
		years = sorted(self.time_toc)
		years.reverse()
		for year in years:
			months = sorted(self.time_toc[year])
			months.reverse()
			for month in months:
				days = sorted(self.time_toc[year][month])
				days.reverse()
				for day in days:
					posts = self.time_toc[year][month][day]
					for post in posts:
						href = post.path.split('/')[1:]
						href = '/'.join([dir for dir in href if dir != ''])
						preview = post.preview_html
						#print preview
						title = post.title
						cache.write(
							'<div class="blog-post">\n\
							<span class="byline"><p>{}.{}.{}</p></span>\n\
							<h1><a href="{}" class="fp-title">{}</a></h1>\n\
							{}<p><a href="{}">Read more</a></p>\n\
							</div>\n'.format(
							day,
							month,
							year,
							href, 
							title, 
							preview, 
							href
						))
		s = cache.getvalue()
		cache.close()
		return s
		
	def construct_page(self, html, template):
		"""
		"""
		# Get template
		template.find_path_back_templates(self.root)
		template.find_path_back_other('../../')
		template.update_html()
		t = template.html
		post = html
		# Insert post html
		page = t.replace('//genson.insertpost//', html)
		page = page.replace('//genson.title//', 'Blog')
		return page
		
	def write_out(self):
		"""
		"""	
		filename = '{}/index.html'.format(self.root)
		with open(filename, 'w') as f:
			f.write('{}'.format(self.html))
			print('Wrote front page: {}'.format(filename))
		return filename
		
	
# Define functions		
def main():
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
		default='template',
		type=str,
		required=False,
		help='Name of the HTML/CSS/JS templates to be used to generate static pages.',
		dest='template'
	)
	args = parser.parse_args()
	# Initialize document tree to keep things neat
	subprocess.call(['rm', '-R', args.output_dir])
	# Get all markdown files in input directory
	md_files = MarkdownFiles(directory=args.input_dir)
	# Gather the template
	template = Template(directory=args.template)
	# Initialize the Markdown parser
	md_parser = markdown.Markdown()
	# Initialize list of blog posts
	post_list = []
	# Go through the MD files and convert to HTML
	for n in md_files.filenames:
		# Create blog post from markdown
		post = BlogPost(
			markdown='{}/{}'.format(args.input_dir, n), 
			rootdir=args.output_dir,
			parser=md_parser,
			template=template
		)
		# Update list of new posts
		post_list.append(post)
	# Convert post list to table of contents
	toc = TableOfContents(posts=post_list, rootdir=args.output_dir, template=template)
	return None
	
# Boilerplate
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit('\n\nGoodbye!\n\n')
	else:
		sys.exit("\n\nSuccess!\n\n")
else:
	pass