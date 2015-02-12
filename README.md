# genson

_Truly your own blog. Truly own your blog_

`genson` is a static blog generator written in Python. It couldn't be easier to use!

Simply write your blog posts in Markdown, then do `python genson.py` and a
blog directory tree magically appears! 

Just upload to your favourite web host, and you're done.

__Why the name `genson`?__ Message me to find out.


## Features
1. Uses Markdown files to create perfect HTML.
2. Organizes your blog's directory tree.
3. Creates a blog front page of posts.
4. Creates a JSON-format search index so you can incorporate site search.
5. Use any HTML, CSS, and JS in a template, in as many files as you want.

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
11. Do `python genson.py -t template`.
12. If the last line in the Terminal was `Success!`, then everything should have gone 
well.
13. Voila! You should have a new directory called `blog` containing the front page and a directory tree of blog posts.

## Advanced use
Try `python genson.py -h` to see more advanced options.

The locations of the Markdown files and templates can be specified, as well as the name of 
the blog root directory.

## To do
1. Add more classes to HTML tags where possible.
2. Add blog tags.
3. Add suggested articles.
4. Package into `setup.py`.

