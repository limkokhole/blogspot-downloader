import os

SUPPORTED_TAGS = {
    'article': ['class'],
    'a': ['href', 'id', 'name'],
    'b': ['id'],
    'big': [],
    'blockquote': ['id'],
    'body': [],
    'br': ['id'],
    'center': [],
    'cite': [],
    'code': [],
    'dd': ['id', 'title'],
    'del': [],
    'dfn': [],
    'div': ['align', 'id', 'bgcolor'],
    'em': ['id', 'title'],
    'figure': [], #hole 
    'font': ['color', 'face', 'id', 'size'],
    'head': [],
    'h1': [],
    'h2': [],
    'h3': [],
    'h4': [],
    'h5': [],
    'h6': [],
    'hr /': ['color', 'id', 'width'],
    'html': [],
    'i': ['class', 'id'],
    'img': ['align', 'border', 'height', 'id', 'src', 'width', 'data-original'],
    'img /': ['align', 'border', 'height', 'id', 'src', 'width', 'data-original'],
    'kbd': [], #hole, https://www.crummy.com/software/BeautifulSoup/bs3/documentation.html#Parsing%20HTML 
    'li': ['class', 'id', 'title'],
    'main': ['class'],
    'ol': ['id'],
    'p': ['align', 'id', 'title'],
    'pre': [],
    's': ['id', 'style', 'title'],
    'samp': [], #hole, https://www.crummy.com/software/BeautifulSoup/bs3/documentation.html#Parsing%20HTML
    'small': ['id'],
    'span': ['bgcolor', 'title'],
    'section': ['class'],
    'strike': ['class', 'id'],
    'strong': ['class', 'id'],
    # Enable this only if needed
    #'style': ['display', 'padding', 'max-height', 'max-width'],
    'sub': ['id'],
    'sup': ['class', 'id'],
    'table': ['width', 'cellspacing', 'cellpadding', 'border',  'align'], #hole
    'td': ['width', 'height', 'bgcolor'], #hole
    'tr': ['width', 'height', 'bgcolor'], #hole
    'u': ['id'],
    'ul': ['class', 'id'],
    'var': []
    }
SINGLETON_TAG_LIST = [
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    ]
xhtml_doctype_string = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'test_files')
EPUB_TEMPLATES_DIR = os.path.join(BASE_DIR, 'epub_templates')
