import re

import bs4

from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution

import constants

try:
  basestring
except NameError:
  basestring = str

def create_html_from_fragment(tag):
    """
    Creates full html tree from a fragment. Assumes that tag should be wrapped in a body and is currently not

    Args:
        tag: a bs4.element.Tag

    Returns:"
        bs4.element.Tag: A bs4 tag representing a full html document
    """

    try:
        assert isinstance(tag, bs4.element.Tag)
    except AssertionError:
        raise TypeError

    #try:
    #    # hole: this is wrong bcoz web browser will auto replace first </html>(if only 2 </html>) with <html>, while <body> still appear.
    #e.g. http://slae.tehwinsam.com/7/assignment7.html
    #    assert tag.find_all('body') == []
    #except AssertionError:
    #    raise ValueError
    #print(tag)
    if tag.find_all('body') == []:
        soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        soup.body.append(tag)
    else:
        soup = BeautifulSoup('<html></html>', 'html.parser')
        soup.html.append(tag)
    #print(soup)
    return soup


def clean(input_string,
          tag_dictionary=constants.SUPPORTED_TAGS):
    """
    Sanitizes HTML. Tags not contained as keys in the tag_dictionary input are
    removed, and child nodes are recursively moved to parent of removed node.
    Attributes not contained as arguments in tag_dictionary are removed.
    Doctype is set to <!DOCTYPE html>.

    Args:
        input_string (basestring): A (possibly unicode) string representing HTML.
        tag_dictionary (Option[dict]): A dictionary with tags as keys and
            attributes as values. This operates as a whitelist--i.e. if a tag
            isn't contained, it will be removed. By default, this is set to
            use the supported tags and attributes for the Amazon Kindle,
            as found at https://kdp.amazon.com/help?topicId=A1JPUWCSD6F59O

    Returns:
        str: A (possibly unicode) string representing HTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    try:
        assert isinstance(input_string, basestring)
    except AssertionError:
        raise TypeError

    #print(input_string)
    root = BeautifulSoup(input_string, 'html.parser')
    #root = BeautifulSoup(input_string, 'lxml') #hole
    #print(root)
    ''' Fixed https://k.sina.cn/article_3960624673_pec12562102700hgxe.html not include all <article> tags
    article_tag = root.find_all('article')
    if article_tag:
        root = article_tag[0]
    '''
    stack = root.findAll(True, recursive=False)
    #print(root)
    while stack:
        current_node = stack.pop()
        #print(current_node)
        child_node_list = current_node.findAll(True, recursive=False)
        #print(child_node_list)
        #print('node name: ' + current_node.name)
        if current_node.name not in tag_dictionary.keys():
            #print('remove it !')
            parent_node = current_node.parent
            current_node.extract()
            for n in child_node_list:
                parent_node.append(n)
        else:
            #print('include it ! ')
            attribute_dict = current_node.attrs
            #print( 'attr dict: ' + repr(attribute_dict) )
            #for attribute in attribute_dict.keys():
            for attribute in list(attribute_dict):
                if attribute not in tag_dictionary[current_node.name]:
                    #if 'Increase memory page and it pointer' in repr(current_node) and 'back the' not in repr(current_node):
                    #    print('tag_dictionary:' +repr(tag_dictionary))
                    #    print('current_node1: ' + repr(current_node))
                    #    print('attribute1: ' + attribute)
                    attribute_dict.pop(attribute)
                    #else:
                    #    if 'Increase memory page and it pointer' in repr(current_node) and 'back the' not in repr(current_node):
                    #        print('tag_dictionary:' +repr(tag_dictionary))
                    #        print('current_node2: ' + repr(current_node))
                    #        print('attribute2: ' + attribute)
        stack.extend(child_node_list)
    #wrap partial tree if necessary
    #print(root)
    if root.find_all('html') == []:
        root = create_html_from_fragment(root)
    # Remove img tags without src attribute
    image_node_list = root.find_all('img')
    for node in image_node_list:
        if not node.has_attr('src'):
            node.extract()
    unformatted_html_unicode_string = root.prettify(encoding='utf-8', formatter='html')
    #unformatted_html_unicode_string = unicode(root.prettify(encoding='utf-8',
    ##                                                        formatter=EntitySubstitution.substitute_html),
    ##                                          encoding='utf-8')
    # fix <br> tags since not handled well by default by bs4
    ##unformatted_html_unicode_string = unformatted_html_unicode_string.replace('<br>', '<br/>')
    # remove &nbsp; and replace with space since not handled well by certain e-readers
    #unformatted_html_unicode_string = unformatted_html_unicode_string.replace(b'&nbsp;', b' ')
    return unformatted_html_unicode_string


def condense(input_string):
    """
    Trims leadings and trailing whitespace between tags in an html document

    Args:
        input_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing HTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    try:
        assert isinstance(input_string, basestring)
    except AssertionError:
        raise TypeError
    removed_leading_whitespace = re.sub('>\s+', '>', input_string).strip()
    removed_trailing_whitespace = re.sub('\s+<', '<', removed_leading_whitespace).strip()
    return removed_trailing_whitespace


def html_to_xhtml(html_unicode_string):
    """
    Converts html to xhtml

    Args:
        html_unicode_string: A (possible unicode) string representing HTML.

    Returns:
        A (possibly unicode) string representing XHTML.

    Raises:
        TypeError: Raised if input_string isn't a unicode string or string.
    """
    #try:
    #    assert isinstance(html_unicode_string, basestring)
    #except AssertionError:
    #    raise TypeError
    root = BeautifulSoup(html_unicode_string, 'html.parser')
    #root = BeautifulSoup(html_unicode_string, 'lxml')
    # Confirm root node is html
    try:
        assert root.html is not None
    except AssertionError:
        raise ValueError(''.join(['html_unicode_string cannot be a fragment.',
                         'string is the following: %s', unicode(root)]))
    # Add xmlns attribute to html node
    root.html['xmlns'] = 'http://www.w3.org/1999/xhtml'
    #unicode_string = unicode(root.prettify(encoding='utf-8', formatter='html'), encoding='utf-8')
    unicode_string = root.prettify(encoding='utf-8', formatter='html')
    # Close singleton tag_dictionary
    #for tag in constants.SINGLETON_TAG_LIST:
    #    print("tag: ", type(tag))
    #    
    #    unicode_string = unicode_string.replace(
    #            '<' + tag + '/>',
    #            '<' + tag + ' />')
    return unicode_string
