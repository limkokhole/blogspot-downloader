# blogspot downloader

This python script download all posts from blogspot and convert into epub or pdf. 

## Why ?

The existing online services either need to paid, has limit of files, need to copy per-page manually, only support rss feed, or only support epub. This python script is free, no files limit as it run in your local machine/ip, download all pages/feed automatically, support both rss and web scraping(some blog rss is private or only one page), support both epub and pdf. It also support custom locale date. The most important thing: this is simple python code and you can feel free to modify it, e.g. custom html color, extra html header/footer, default directory ... etc :)

## How to setup
    git clone https://github.com/limkokhole/blogspot-to-pdf-downloader.git

    pip2 install -r requirements_py2.txt #python 2

    OR

    pip3 install -r requirements_py3.txt #python 3

    In ubuntu, run `sudo apt install wkhtmltopdf`

## How to run

    python blogspot_downloader.py [url]

    OR

    $ python blogspot_downloader.py --help

    usage: blogspot_downloader.py [-h] [-a] [-s] [-d] [-p] [-l LOCALE] [-f FEED]                                                                          
                                  [url]                                                                                                                   

    Blogspot Downloader

    positional arguments:
      url                   Blogspot url

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all             Display website mode instead of rss feed mode. Only
                            support blogspot website but you can try yuor luck in
                            other site too
      -s, --single          Download based on provided url year/month instead of
                            entire blog, will ignored in rss feed mode and
                            --print_date
      -d, --print_date      Print main date info without execute anything
      -p, --pdf             Output in PDF instead of EPUB but might failed in some
                            layout
      -l LOCALE, --locale LOCALE
                            Date translate to desired locale, e.g. -l zh_CN.UTF-8
                            will shows date in chinese
      -f FEED, --feed FEED  Direct pass full rss feed url. e.g. python
                            blogspot_downloader.py http://www.ulduzsoft.com/feed/
                            -f http://www.ulduzsoft.com/feed/. Note that it may
                            not able to get previous rss page in non-blogspot
                            site.


It will asked the blogspot url if you don't pass [url] in command option.

Use -f rss_feed_url to download from rss feed, or -a webpage_url to download from webpage. Tips: you may lucky to find feed url by right-click on the webpage and choose "View Page Source", then search for "rss" keyword. Note that rss_feed / path might has impact to narrow the scope of feed, e.g. https://example.com/2018/05/ might narrow the feed only for may only, and https://example.com/2018/ might narrow the feed for year 2018.

Not all blogs works in -p pdf mode, you will quickly noticed this if you found duplicated layout for first few pages, then you can ctrl+c to stop it. Try feed_feed_url instead in this case, or download epub only.

This script designate in Linux and never test in Windows. This script also not designate run in multi process since it will remove /tmp trash file.

To make pypub works in python 3, read how_to_make_epub_work_in_python3.guide to change it manually yourself, or simply fork the module from https://github.com/limkokhole/pypub . Sometime pypub in python 3 OR pdf able to shows image, but not pypub in python 2, e.g. https://medium.com/feed/bugbountywriteup , or python 2 able to shows but not in python 3, so you might need to test to get the best output on certain site.

ePUB file can edit manually. Simply change name to .zip, unzip it, edit the xhtml, and (inside epub directory) do `zip -rX ../<epub direcory name>.epub minetype.txt META-INF/ OEBPS/` to repack it easily.  I recommend Kchmviewer viewer and Sigli, but if it doesn't open since it may too strict in xhtml syntax, then you can try other viewer in this case (Sigli will try auto fix for you), and please don't feel hesitate to open a issue ticket.  

download non-blogspot site as rss feed in pdf:  

![medium](/medium.png?raw=true "download non-blogspot site as rss feed in pdf")  

download blogspot site as rss feed in pdf without file limits:

![google](/google.png?raw=true "download blogspot site as rss feed in pdf without file limits")  

download blogspot site as web scraping in ePUB:

![eat](/eat.png?raw=true "download blogspot site as web scraping in ePUB")

download blogspot site as rss feed in ePUB, plus custom locale:  

![locale](/locale.png?raw=true "download blogspot site as rss feed in ePUB, plus custom locale")

pdf keep color, while ePUB don't:  

![color](/color.png?raw=true "pdf keep color, while ePUB don't")

## Demonstration video (Click image to play at YouTube): ##
[![watch in youtube](https://i.ytimg.com/vi/B6QzTmMglEo/hqdefault.jpg)](https://www.youtube.com/watch?v=B6QzTmMglEo "Blogspot_downloader")


