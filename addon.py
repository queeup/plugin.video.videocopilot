# -*- coding: utf-8 -*-

# Imports
from BeautifulSoup import SoupStrainer, BeautifulSoup as BS
import hashlib
import os
import shutil
import tempfile
import time
import errno
import sys
import re
import urllib
import urllib2
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# DEBUG
DEBUG = False

__addon__ = xbmcaddon.Addon(id='plugin.video.videocopilot')
__info__ = __addon__.getAddonInfo
__plugin__ = __info__('name')
__version__ = __info__('version')
__icon__ = __info__('icon')
__cachedir__ = __info__('profile')

CACHE_1MINUTE = 60
CACHE_1HOUR = 3600
CACHE_1DAY = 86400
CACHE_1WEEK = 604800
CACHE_1MONTH = 2592000

CACHE_TIME = CACHE_1DAY


class Main:
  def __init__(self):
    if ("action=play" in sys.argv[2]):
      self.play()
    else:
      self.list_contents()

  def list_contents(self):
    if DEBUG:
      self.log('list_contents')
    baseurl = 'http://www.videocopilot.net/tutorials/'
    # Parse HTML results page...
    html = fetcher.fetch(baseurl)
    soup = BS(html, parseOnlyThese=SoupStrainer('div', 'tutorials-all-container'))

    for entry in soup.findAll('div', 'tutorials-all-item'):
      title = entry('div', 'tutorials-all-item-title')[0].a.string
      time = entry('div', 'tutorials-all-item-time')[0].string
      thumb = entry('a', 'tutorials-all-image')[0]['style'].replace('background:url(', '').replace(')', '').replace('/popular/', '/large/')
      url = entry('a', 'tutorials-all-image')[0]['href'].replace('tutorials', 'tutorial')
      desc = entry('div', 'tutorials-all-item-subtitle')[0].string.strip()
      studio = 'www.videocopilot.net'
      director = 'Andrew Kramer'

      # Add Videos to XBMC
      listitem = xbmcgui.ListItem(title, iconImage='DefaultVideoBig.png', thumbnailImage=thumb)
      listitem.setInfo(type='video',
                       infoLabels={'title': title,
                                   'duration': time,
                                   'plot': desc,
                                   'plotoutline': desc,
                                   'director': director,
                                   'studio': studio,
                                   'copyright': director,
                                   'tvshowtitle': 'Video Copilot'})
      url = "%s?action=play&url=%s" % \
            (sys.argv[0], urllib.quote_plus(url))
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
    # Sort methods and content type...
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    #xbmcplugin.addSortMethod(handle=int(sys.argv[ 1 ]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def play(self):
    if DEBUG:
      self.log('play()')
    # Get current list item details...
    title = unicode(xbmc.getInfoLabel("ListItem.Title"), "utf-8")
    thumbnail = xbmc.getInfoImage("ListItem.Thumb")
    plot = unicode(xbmc.getInfoLabel("ListItem.Plot"), "utf-8")
    director = unicode(xbmc.getInfoLabel("ListItem.Director"), "utf-8")
    studio = unicode(xbmc.getInfoLabel("ListItem.Studio"), "utf-8")
    # Parse HTML results page...
    html = urllib.urlopen(self.arguments('url')).read()
    # Get FLV video...
    match = re.compile('so.addVariable\(\'file\'\,\'(.+?)\'\)\;').findall(html)
    for _url in match:
      video_url = _url
    # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
    listitem = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    # set the key information
    listitem.setInfo('video', {'title': title,
                               'director': director,
                               'plot': plot,
                               'plotoutline': plot,
                               'studio': studio})
    # Play video...
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(video_url, listitem)

  def arguments(self, arg):
    _arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(_arguments[arg])

  def log(self, description):
    xbmc.log("[ADD-ON] '%s v%s': '%s'" % (__plugin__, __version__, description), xbmc.LOGNOTICE)


class DiskCacheFetcher:
  def __init__(self, cache_dir=None):
    # If no cache directory specified, use system temp directory
    if cache_dir is None:
      cache_dir = tempfile.gettempdir()
    if not os.path.exists(cache_dir):
      try:
        os.mkdir(cache_dir)
      except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(cache_dir):
          # File exists, and it's a directory,
          # another process beat us to creating this dir, that's OK.
          pass
        else:
          # Our target dir is already a file, or different error,
          # relay the error!
          raise
    self.cache_dir = cache_dir

  def fetch(self, url, max_age=CACHE_TIME):
    # Use MD5 hash of the URL as the filename
    print url
    filename = hashlib.md5(url).hexdigest()
    filepath = os.path.join(self.cache_dir, filename)
    if os.path.exists(filepath):
      if int(time.time()) - os.path.getmtime(filepath) < max_age:
        if DEBUG:
          print 'file exists and reading from cache.'
        return open(filepath).read()
    # Retrieve over HTTP and cache, using rename to avoid collisions
    if DEBUG:
      print 'file not yet cached or cache time expired. File reading from URL and try to cache to disk'
    data = urllib2.urlopen(url).read()
    fd, temppath = tempfile.mkstemp()
    fp = os.fdopen(fd, 'w')
    fp.write(data)
    fp.close()
    shutil.move(temppath, filepath)
    return data

fetcher = DiskCacheFetcher(xbmc.translatePath(__cachedir__))

if __name__ == '__main__':
  Main()