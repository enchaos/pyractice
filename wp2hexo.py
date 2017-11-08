import xml.etree.ElementTree as ET
import sys, os, os.path, argparse
import html2text
from shutil import rmtree as rm_dir_all


class Blog:
	def __init__(self, title):
		self.title = title
		self.description = ''
		self.categories = []
		self.tags = []
		self.articles = None

	def __str__(self):
		return ('''
-----------------
Blog: %s
Desc: %s
Cats: %s
Tags: %s
-----------------
		''' % (self.title, self.description, self.categories, self.tags))

class Article:
	def __init__(self, post_name):
		if not post_name: post_name = '_[no title]'
		self.post_name = post_name
		self.is_page = False # false=Post, true=Page wp:post_type
		self.is_draft = False
		self.title = ''
		#not really 'link' atti in xml, but a reflection of this post history
		self.link = ''
		self.content_html = ''
		self.content_md = ''
		self.post_date = ''
		self.post_id = ''
		self.post_type = '' #publish|limited with password|private
		self.category = ''
		self.tags = []
		self.saved = False

	def __str__(self):
		return ('''
		================
		Post Name: %s
		Is Page: %s
		Is Draft: %s
		Title: %s
		Link: %s
		Post Date: %s
		Post ID: %s
		Post Type: %s
		Category: %s
		Tags: %s
		================
		''' % (
		self.post_name,
		self.is_page,
		self.is_draft,
		self.title,
		self.link,
		self.post_date,
		self.post_id,
		self.post_type,
		self.post_type,
		self.tags
		))

	def hexo_content(self):
		tag_str = ''
		for t in self.tags:
			tag_str += ' - '
			tag_str += t
			tag_str += '\n'

		if self.is_draft:
			hexo_md = '---\ntitle: "%s"\ntags: \n%sid: %s\n---\n\n%s'
			return hexo_md % (self.title, tag_str, self.post_id, self.content_md)
		elif self.is_page:
			hexo_md = '---\ntitle: "%s"\ndate: %s\nid: %s\n---\n\n%s'
			return hexo_md % (self.title, self.post_date, self.post_id, self.content_md)
		else:
			hexo_md = '---\ntitle: "%s"\ndate: %s\ntags: \n%sid: %s\ncategories:\n - %s\n---\n\n%s'
			return hexo_md % (self.title, self.post_date, tag_str, self.post_id, self.category, self.content_md)


def parse_blog(root, xmlns):
	blog = Blog(root[0].find('title').text)
	blog.description = root[0].find('description').text
	for cat in root[0].findall('wp:category', xmlns):
		blog.categories.append(cat.find('wp:cat_name', xmlns).text)
	for tag in root[0].findall('wp:tag', xmlns):
		blog.tags.append(tag.find('wp:tag_name', xmlns).text)
	return blog

def parse_items(root, xmlns):
	articles = []
	for item in root.iter('item'):
		if item.find('title').text and item.find('content:encoded', xmlns).text:
			article = Article(item.find('wp:post_name', xmlns).text)
			article.is_page = (item.find('wp:post_type', xmlns).text == 'page')
			article.is_draft = (item.find('wp:status', xmlns).text != 'publish')
			article.title = item.find('title').text
			article.link = item.find('guid').text
			article.content_html = item.find('content:encoded', xmlns).text
			if article.content_html:
				article.content_md = html2text.html2text(article.content_html)
			article.post_date = item.find('wp:post_date', xmlns).text
			article.post_id = item.find('wp:post_id', xmlns).text
			article.post_type = item.find('wp:post_type', xmlns).text
			cats = item.findall('category')
			if len(cats) > 0:
				for category in cats:
					if category.get('domain')=='category':
						article.category = category.text
					if category.get('domain')=='post_tag':
						article.tags.append(category.text)
			articles.append(article)
	return articles

def prepare_folders(location):

	if not location: location = 'hexo'

	if os.path.exists(os.path.join(location, 'source')):
		rm_dir_all(os.path.join(location, 'source'))
		print("Source Folder: [%s] cleared." % os.path.join(location, 'source'))

	os.makedirs(location, exist_ok=True)
	os.makedirs(os.path.join(location, 'source', '_posts'), exist_ok=True)
	os.makedirs(os.path.join(location, 'source', '_drafts'), exist_ok=True)

	hexo_paths = {
		'top': location,
		'source': os.path.join(location, 'source'),
		'posts': os.path.join(location, 'source', '_posts'),
		'drafts': os.path.join(location, 'source', '_drafts'),
	}
	return hexo_paths

def get_blog_from_wordpress(wp_xml):
	if os.path.exists(wp_xml):
		xmlns = dict([elem for evt, elem in ET.iterparse(wp_xml, events=['start-ns'])])
		root = ET.parse(wp_xml).getroot()
		blog = parse_blog(root, xmlns)
		items = parse_items(root, xmlns)
		blog.articles = items
		return blog
	else:
		sys.exit("Can't find xml!")

def save_blog_to_hexo(blog, hexo_paths):
	saved = False
	with open(os.path.join(hexo_paths['top'], blog.title + '.txt'), 'w', encoding='utf-8') as bf:
		bf.write(str(blog))
		for a in blog.articles:
			print('%s - "%s.md"' % (a.title, a.post_name))
			bf.write('\n%s: %s' % (a.post_date, a.title))
			if a.is_draft:
				with open(os.path.join(hexo_paths['drafts'], a.post_name + '.md'), 'w', encoding='utf-8') as f:
					f.write(a.hexo_content())
			elif a.is_page:
				os.makedirs(os.path.join(hexo_paths['source'], a.post_name), exist_ok=True)
				with open(os.path.join(hexo_paths['source'], a.post_name, 'index.md'), 'w', encoding='utf-8') as f:
					f.write(a.hexo_content())
			else:
				with open(os.path.join(hexo_paths['posts'], a.post_name + '.md'), 'w', encoding='utf-8') as f:
					f.write(a.hexo_content())
	saved = True
	return saved

def main():

	parser = argparse.ArgumentParser(description='From Wordpress export xml to Hexo Markdown files.')

	parser.add_argument('wp_xml', help='Wordpress exported xml as source')
	parser.add_argument('location', help='Hexo blog top folder as destination, if not specified, "hexo" will be created at current directory')

	args = parser.parse_args()

	hexo_paths = prepare_folders(args.location)
	blog = get_blog_from_wordpress(args.wp_xml)

	print("Parsing is done, preparing to save~~")
	saved = save_blog_to_hexo(blog, hexo_paths)
	if saved: print('Save to Hexo md files are done: [%s]' % os.path.abspath(hexo_paths['top']))



if(__name__=='__main__'):
	main()
