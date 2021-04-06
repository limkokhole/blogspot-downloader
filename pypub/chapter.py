import html #cgi.escape deprecated since py 3.2 , https://docs.python.org/3/whatsnew/3.8.html#api-and-feature-removals
import codecs
import imghdr
import os
import shutil
import tempfile
import http
import urllib
#import urlparse
from urllib.parse import urlparse
import uuid
import bs4
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
import requests

import clean

# hole
#import sys
#import logging
#logging.basicConfig(level=logging.DEBUG, format="%(message)s")
'''
if sys.version_info < (3,):
    from cookielib import Cookie, MozillaCookieJar, DefaultCookiePolicy, CookieJar, FileCookieJar
else:
    from http.cookiejar import Cookie, MozillaCookieJar, DefaultCookiePolicy, CookieJar, FileCookieJar

# rf: https://docs.python.org/2.4/lib/cookielib-examples.html
class CustomCookiePolicy(DefaultCookiePolicy):

    def return_ok(self, cookie, request):
        print(5555)

    #def return_ok_expires(self, cookie, request):
    #    print(77777)
    #    if cookie.is_expired(self._now):
    #        _debug("   cookie expired but still return True")
    #    return True

policy = CustomCookiePolicy()

#/usr/lib/python3.6/http/cookiejar.py hard code top `debug = True` to print _debug()
def load_cookies(fname):

    def load_cookies_from_mozilla(fname):

        cj = CookieJar(policy=policy)
        #ns_cookiejar = FileCookieJar(filename=fname, policy=policy)
        ns_cookiejar = MozillaCookieJar(filename=fname, policy=policy)
        #ns_cookiejar = MozillaCookieJar(filename=fname, policy=policy)
        ns_cookiejar.load(ignore_discard=True, ignore_expires=True) #, ignore_discard=True, ignore_expires=True)
        return ns_cookiejar

    return load_cookies_from_mozilla(fname)
'''

class NoUrlError(Exception):
    def __str__(self):
        return 'Chapter instance URL attribute is None'


class ImageErrorException(Exception):
    def __init__(self, image_url):
        self.image_url = image_url

    def __str__(self):
        return 'Error downloading image from ' + self.image_url


def get_image_type(url):
    url = url.lower()
    for ending in ['.jpg', '.jpeg', '.gif', '.png', '.bmp']:
        if url.endswith(ending) or ((ending + '?') in url):
            return ending
    else:
        try:
            f, temp_file_name = tempfile.mkstemp()
            try:
                urllib.request.urlretrieve(url, temp_file_name)
            except http.client.InvalidURL:
                # Remove newline in url.
                # Test case: https://www.chinapress.com.my/20210406/%e5%a4%9f%e5%8a%9b%e6%9c%89%e9%92%b1%ef%bc%81-%e5%ae%b6%e8%97%8f350%e4%b8%87%e7%8e%b0%e9%87%91-%e5%9d%90%e6%8b%a5%e6%b8%b8%e8%89%87%e3%80%81%e7%9b%b4%e5%8d%87%e6%9c%ba/ -> contains 'https://www.facebook.com/tr?id=469667556766095&ev=pageview\n&noscript=1' (repr(url))
                # https://stackoverflow.com/a/39416125/1074998
                urllib.request.urlretrieve(re.sub(r'[\x00-\x1f\x7f-\x9f]', '', url), temp_file_name)
            image_type = imghdr.what(temp_file_name)
            return image_type
        except IOError:
            return None


def save_image(image_url, image_directory, image_name):
    """
    Saves an online image from image_url to image_directory with the name image_name.
    Returns the extension of the image saved, which is determined dynamically.

    Args:
        image_url (str): The url of the image.
        image_directory (str): The directory to save the image in.
        image_name (str): The file name to save the image as.

    Raises:
        ImageErrorException: Raised if unable to save the image at image_url
    """
    image_type = get_image_type(image_url)
    if image_type is None:
        raise ImageErrorException(image_url)
    full_image_file_name = os.path.join(image_directory, image_name + '.' + image_type)
    try:
        # urllib.urlretrieve(image_url, full_image_file_name)
        with open(full_image_file_name, 'wb') as f:
            user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
            try:
                # test case: 'https://www.raychase.net/1418' 's 'https://www.raychase.net/wp-content/uploads/2019/10/极客时间.png'
                # unicode header need encode first or else throws "UnicodeEncodeError: 'latin-1' codec" error in python3.6/http/client.py
                # rf: https://stackoverflow.com/questions/6289474/
                img_url_h = image_url.encode('utf-8')
            except UnicodeEncodeError:
                img_url_h = image_url
            request_headers = {'User-Agent': user_agent, 'Referer': img_url_h} #hole
            requests_object = requests.get(image_url, headers=request_headers, allow_redirects=True, timeout=30)
            try:
                content = requests_object.content
                # Check for empty response
                f.write(content)
            except AttributeError:
                raise ImageErrorException(image_url)
    except IOError:
        raise ImageErrorException(image_url)
    return image_type


def _replace_image(image_url, image_tag, ebook_folder,
                   image_name=None):
    """
    Replaces the src of an image to link to the local copy in the images folder of the ebook. Tightly coupled with bs4
        package.

    Args:
        image_url (str): The url of the image.
        image_tag (bs4.element.Tag): The bs4 tag containing the image.
        ebook_folder (str): The directory where the ebook files are being saved. This must contain a subdirectory
            called "images".
        image_name (Option[str]): The short name to save the image as. Should not contain a directory or an extension.
    """
    try:
        assert isinstance(image_tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError("image_tag cannot be of type " + str(type(image_tag)))
    if image_name is None:
        image_name = str(uuid.uuid4())
    try:
        image_full_path = os.path.join(ebook_folder, 'images')
        assert os.path.exists(image_full_path)
        image_extension = save_image(image_url, image_full_path,
                                     image_name)
        image_tag['src'] = 'images' + '/' + image_name + '.' + image_extension
    except ImageErrorException:
        image_tag.decompose()
    except AssertionError:
        raise ValueError('%s doesn\'t exist or doesn\'t contain a subdirectory images' % ebook_folder)
    except TypeError:
        image_tag.decompose()

from urllib.parse import urljoin
class Chapter(object):
    """
    Class representing an ebook chapter. By and large this shouldn't be
    called directly but rather one should use the class ChapterFactor to
    instantiate a chapter.

    Args:
        content (str): The content of the chapter. Should be formatted as
            xhtml.
        title (str): The title of the chapter.
        url (Option[str]): The url of the webpage where the chapter is from if
            applicable. By default this is None.

    Attributes:
        content (str): The content of the ebook chapter.
        title (str): The title of the chapter.
        url (str): The url of the webpage where the chapter is from if
            applicable.
        html_title (str): Title string with special characters replaced with
            html-safe sequences
    """
    def __init__(self, content, title, url=None):
        self._validate_input_types(content, title)
        self.title = title
        self.content = content
        self._content_tree = BeautifulSoup(self.content, 'html.parser')
        #print(self._content_tree) #pretty already
        self.url = url
        self.html_title = html.escape(self.title, quote=True)

    def write(self, file_name):
        """
        Writes the chapter object to an xhtml file.

        Args:
            file_name (str): The full name of the xhtml file to save to.
        """
        try:
            assert file_name[-6:] == '.xhtml'
        except (AssertionError, IndexError):
            raise ValueError('filename must end with .xhtml')
        with open(file_name, 'wb') as f:
            #f.write(self.content.encode('utf-8'))
            f.write(self.content)

    def _validate_input_types(self, content, title):
        #try:
        #    assert isinstance(content, basestring)
        #except AssertionError:
        #    raise TypeError('content must be a string')
        #try:
        #    assert isinstance(title, basestring)
        #except AssertionError:
        #    raise TypeError('title must be a string')
        try:
            assert title != ''
        except AssertionError:
            raise ValueError('title cannot be empty string')
        try:
            assert content != ''
        except AssertionError:
            raise ValueError('content cannot be empty string')

    def get_url(self):
        if self.url is not None:
            return self.url
        else:
            raise NoUrlError()

    def _get_image_urls(self):
        image_nodes = self._content_tree.find_all('img')
        raw_image_urls = []
        image_nodes_filtered = []
        for node in image_nodes:
            if node.has_attr('data-original'):
                raw_image_urls.append(node['data-original'])
                image_nodes_filtered.append(node)
            elif node.has_attr('src'):
                raw_image_urls.append(node['src'])
                image_nodes_filtered.append(node)
                
        #raw_image_urls = [node['src'] for node in image_nodes if node.has_attr('src')]
        #full_image_urls = [urlparse.urljoin(self.url, image_url) for image_url in raw_image_urls]
        full_image_urls = [urljoin(self.url, image_url) for image_url in raw_image_urls]

        #image_nodes_filtered = [node for node in image_nodes if node.has_attr('src')]
        #print(image_nodes_filtered)
        #print(full_image_urls)
        return zip(image_nodes_filtered, full_image_urls)

    def _replace_images_in_chapter(self, ebook_folder):
        image_url_list = self._get_image_urls()
        for image_tag, image_url in image_url_list:
            _replace_image(image_url, image_tag, ebook_folder)
        unformatted_html_unicode_string = self._content_tree.prettify(encoding='utf-8', formatter='html')
        #unformatted_html_unicode_string = unicode(self._content_tree.prettify(encoding='utf-8',
        #                                                                      formatter=EntitySubstitution.substitute_html),
        #                                          encoding='utf-8')
        #unformatted_html_unicode_string = unformatted_html_unicode_string.replace('<br>', '<br/>')
        self.content = unformatted_html_unicode_string

import re
def hole_meta_encoding(soup):
    if soup and soup.meta:
        encod = soup.meta.get('charset')
        if encod == None:
            encod = soup.meta.get('content-type')
            if encod == None:
                content = soup.meta.get('content')
                match = re.search('charset=(.*)', content)
                if match:
                    encod = match.group(1)
                else:
                    return None #raise ValueError('unable to find encoding')
        return encod



class ChapterFactory(object):
    """
    Used to create Chapter objects.Chapter objects can be created from urls,
    files, and strings.

    Args:
        clean_function (Option[function]): A function used to sanitize raw
            html to be used in an epub. By default, this is the pypub.clean
            function.
    """

    def __init__(self, clean_function=clean.clean):
        self.clean_function = clean_function
        #UA causes too old web browser page, e.g. https://huanlan.zhihu.com/p/12345
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/1000000.0'
        self.request_headers = {'User-Agent': user_agent}

    def create_chapter_from_url(self, url, title=None):
        """
        Creates a Chapter object from a url. Pulls the webpage from the
        given url, sanitizes it using the clean_function method, and saves
        it as the content of the created chapter. Basic webpage loaded
        before any javascript executed.

        Args:
            url (string): The url to pull the content of the created Chapter
                from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the webpage at the given
                url and whose title is that provided or inferred from the url

        Raises:
            ValueError: Raised if unable to connect to url supplied
        """
        try:
            #print(self.request_headers) #hole

            try: 
                # in case unicode in url
                img_url_referer = url.encode('utf-8')
            except UnicodeEncodeError:
                img_url_referer = url

            self.request_headers['Referer'] = img_url_referer #hole
            #print(self.request_headers) #hole
            #cookie_f = '/home/xiaobai/Downloads/cookies/cookies.txt'
            #cookie_f = '/home/xiaobai/Downloads/cookies/cookies_july26.txt'
            # OR `nc -l -p 52134` to check ( < ~/Downloads/my.res to reply), just sed to replace host of cookies.txt
            #url = 'https://httpbin.org/cookies'
            #url = 'http://127.0.0.1:52134'
            #print(url)

            s = requests.Session()

            s.headers = self.request_headers
            s.allow_redirects = True
            s.timeout = 30

            #s.cookies = load_cookies(cookie_f)
            #s.cookies.set_policy(policy=policy)

            #print(dir(s))
            #print(s.cookies)

            import trace
            #print("sys path: ", sys.prefix, sys.exec_prefix)
            '''
            tracer = trace.Trace(
                trace=1,
                #ignoredirs=[sys.prefix, sys.exec_prefix] )
                ignoredirs=[ '/usr/lib/python3/',  '/usr/lib/python3.6/', '/usr/lib/python3.8/',
                '/home/xiaobai/.local/lib/python3.6/site-packages/lxml/', 
                    ]
                #count=1)
            )
            '''
            #request_object = tracer.runfunc( requests.get, url, headers=self.request_headers, allow_redirects=True
            #                , timeout = 30, cookies=load_cookies(cookie_f) )
            #request_object =  requests.get( url, headers=self.request_headers, allow_redirects=True
            #                , timeout = 30, cookies=load_cookies(cookie_f) )

            '''
            def update(self, other):
                """Updates this jar with cookies from another CookieJar or dict-like"""
                if isinstance(other, requests.compat.cookielib.CookieJar):
                    for cookie in other:
                        self.set_cookie(copy.copy(cookie))
                else:
                    super(RequestsCookieJar, self).update(other)
            '''
            #import mock
            #with mock.patch.object(requests.cookies.RequestsCookieJar, 'update', lambda *args, **kwargs: 0):
            #with mock.patch.object(requests.cookies.RequestsCookieJar, 'update', update):
            #request_object = tracer.runfunc(s.get, url)
            request_object = s.get(url)

            #print(request_object.cookies)
            #print(request_object.text)

        except (requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError):
            raise ValueError("%s is an invalid url or no network connection" % url)
        except requests.exceptions.SSLError:
            raise ValueError("Url %s doesn't have valid SSL certificate" % url)
        #unicode_string = request_object.text
        return self.create_chapter_from_string(None, url, title, request_object=request_object)

    def create_chapter_from_file(self, file_name, url=None, title=None):
        """
        Creates a Chapter object from an html or xhtml file. Sanitizes the
        file's content using the clean_function method, and saves
        it as the content of the created chapter.

        Args:
            file_name (string): The file_name containing the html or xhtml
                content of the created Chapter
            url (Option[string]): A url to infer the title of the chapter from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the given file
                and whose title is that provided or inferred from the url
        """
        with codecs.open(file_name, 'r', encoding='utf-8') as f:
            content_string = f.read()
        return self.create_chapter_from_string(content_string, url, title)

    def create_chapter_from_string(self, html_string, url=None, title=None, request_object=None):
        """
        Creates a Chapter object from a string. Sanitizes the
        string using the clean_function method, and saves
        it as the content of the created chapter.

        Args:
            html_string (string): The html or xhtml content of the created
                Chapter
            url (Option[string]): A url to infer the title of the chapter from
            title (Option[string]): The title of the created Chapter. By
                default, this is None, in which case the title will try to be
                inferred from the webpage at the url.

        Returns:
            Chapter: A chapter object whose content is the given string
                and whose title is that provided or inferred from the url
        """
        if request_object:
            # Test case: https://new.qq.com/omn/20180816/20180816A0A0D0.html which return headers "content-type: text/html; charset=GB2312"
            # ... shouldn't make it utf-8
            if not request_object.encoding: # just in case, default depends on header content-type(alternative to html meta)
                request_object.encoding = 'utf-8'
                html_string = request_object.text
            else:
                # test case(ISO-8859-1): http://castic.xiaoxiaotong.org/2019/studentDetails.html?77061
                try:
                    html_string = request_object.text.encode(request_object.encoding).decode('utf-8')
                except UnicodeDecodeError:
                    # test case: https://www.dawuxia.net/forum.php?mod=viewthread&tid=1034211
                    html_string = request_object.text
        elif not html_string: #if 404, request_object will None
            html_string = '<html></html>'
        #print(html_string)
        clean_html_string = self.clean_function(html_string)
        #print(clean_html_string)
        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)
        if title:
            pass
        else:
            try:
                if request_object:
                    root = BeautifulSoup(html_string, 'html.parser')
                    meta_encoding = hole_meta_encoding(root)
                    #print(meta_encoding)
                    if meta_encoding and (meta_encoding.lower() != 'utf-8'):
                        print('Encoding to meta encoding: ' + repr(meta_encoding))
                        request_object.encoding = meta_encoding
                        html_string = request_object.text
                        root = BeautifulSoup(html_string, 'html.parser')
                        clean_html_string = self.clean_function(html_string)
                        clean_xhtml_string = clean.html_to_xhtml(clean_html_string)
                    
                else:
                    root = BeautifulSoup(html_string, 'html.parser')

                title_node = root.title
                if title_node is not None:
                    #title = unicode(title_node.string)
                    title = title_node.string
                    if title == None:
                        title = 'Unknown title'
                else:
                    raise ValueError
            except (IndexError, ValueError):
                title = 'Ebook Chapter'
        #print(clean_xhtml_string)
        return Chapter(clean_xhtml_string, title, url)

create_chapter_from_url = ChapterFactory().create_chapter_from_url
create_chapter_from_file = ChapterFactory().create_chapter_from_file
create_chapter_from_string = ChapterFactory().create_chapter_from_string
