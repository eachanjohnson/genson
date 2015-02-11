# genson

_Truly own your blog_

`genson` is a static blog generator written in Python. It couldn't be easier to use!

Simply write your blog posts in easy-to-use Markdown, then do `python genson.py` and a
blog directory tree magically appears! 

Just upload to your favourite web host, and you're done.

__Why `genson`?__ My surname's Johnson, and this is a _gen_erator. Funny, huh?


## Features
1. Uses easy Markdown files to create perfect HTML.
2. Organizes your blog in a neat directory tree.
3. Auto-creates a table of contents and blog front page.
4. Incorporates existing templates and maintains links to JavaScript and CSS.

## Requirements
1. Python 2.\*
2. Ability to `cd` in the Terminal.

## Instructions
1. Keep the file `genson.py` in the root directory of your website.
2. Write a blog post in Markdown. Try it out [here](http://spec.commonmark.org/dingus/).
3. The first line of your post must be the title.
4. You can include the dates and times of creation and editing of the post by entering 
`//genson.created//` and `//genson.modified//` where you want them on the page.
5. Indicate what part, if any, you want to be the preview on your front page with two 
lines, one saying `//genson.startpreview//`, the other `//genson.endpreview//`.
6. Save your post with the Markdown file extension, `.md`, in the root directory of your
website.
7. Gather any HTML templates (if using them) and their resources (JS and CSS) a directory called `template`.
8. In the HTML template, replace the JS and CSS paths with `//genson.path//`.
9. In the HTML template, where you want the blog post to go, enter `//genson.insertpost//`.
10. In the terminal, `cd` to the root directory of your website.
11. If you're using the templates, do `python genson.py -t template`.
12. If not using a template, do `python genson.py`.
13. If the last line in the Terminal was `Success!`, then everything should have gone 
well.
14. Voila! You should have a new directory called `blog` containing the Table of Contents
in `toc.html`, the front page in `index.html`, and your individual posts in the 
sub-directories.

## Advanced use
Try `python genson.py -h` to see more advanced options.

The locations of the Markdown files and templates can be specified, as well as the name of 
the blog root directory.

## To do
1. Add more classes to HTML tags where possible.
2. Add blog tags.
3. Add suggested articles.
4. Search.
5. Package into `setup.py`.

