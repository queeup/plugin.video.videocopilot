# -*- coding: utf-8 -*-

# Debug
Debug = False

# Imports
import os, sys, re, urllib, urllib2
import md5, os, shutil, tempfile, time, errno
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from BeautifulSoup import BeautifulSoup as BS

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
      self.start()

  def start(self):
    if Debug: self.LOG('List Videos')
    baseurl = 'http://www.videocopilot.net/tutorials/'
    results = []
    # Parse HTML results page...
    html = fetcher.fetch(baseurl, CACHE_TIME)
    soup = BS(html)
    table_forumline_altlist = soup.findAll("div", { "style" : re.compile('float:left;border-left:solid 1px.+?;border-bottom:solid 1px.+?;border-right:solid 1px.+?;height:92px;width:.+?;padding-top:18px;background:url.+?') })
    for table_forumline_altlist_tr in table_forumline_altlist :
      table_forumline_altlist_tr_tds = table_forumline_altlist_tr.findAll(["div"])
      url = table_forumline_altlist_tr_tds[0].a["href"]
      thumb = table_forumline_altlist_tr_tds[0].a.img["src"]
      date = table_forumline_altlist_tr_tds[1].string
      name = table_forumline_altlist_tr_tds[3].a.string
      desc = table_forumline_altlist_tr_tds[5].renderContents()
      desc = re.sub("&bull;", '', str(desc))
      desc = re.sub("<br />", '.', str(desc))
      desc = re.sub("\t*", '', str(desc))
      desc = re.sub("\n", '', str(desc))
      #results.append((thumb, name, url, date, desc))
      #for thumb, name, url, date, desc in results:
      _thumb = thumb.replace('list', 'large')
      _name = name
      _desc = desc
      _url = url.replace('tutorials', 'tutorial')
      date = re.sub('th,|st,|rd,|nd,', '', date)
      _date, _year = self.convertTextToDate(date)
      _studio = 'www.videocopilot.net'
      _director = 'Andrew Kramer'
      #_year = 0
      #_year = int(_date.split(".")[ 2 ])
      #_year = re.compile('(\d{4})').findall(date)
      #_year = year[0]

      # Add Videos to XBMC
      listitem = xbmcgui.ListItem(_name, iconImage="DefaultVideoBig.png", thumbnailImage=_thumb)
      listitem.setInfo(type="Video",
                       infoLabels={"Title" : _name,
                                   "Label" : _name,
                                   "Plot" : _desc,
                                   "PlotOutline": _desc,
                                   "Director" : _director,
                                   "Year" : _year,
                                   "Date" : _date,
                                   "Studio" : _studio,
                                   "copyright": _director,
                                   "tvshowtitle" : 'Video Copilot' })
      url = "%s?action=play&url=%s" % \
              (sys.argv[ 0 ], urllib.quote_plus(_url))
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[ 1 ]), url=url, listitem=listitem, isFolder=False)
    # Sort methods and content type...
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    # TODO: Date and Year not showin on screen.
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    #xbmcplugin.addSortMethod(handle=int(sys.argv[ 1 ]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def play(self):
    if Debug: self.LOG('Play Video')
    # Get current list item details...
    title = unicode(xbmc.getInfoLabel("ListItem.Title"), "utf-8")
    thumbnail = xbmc.getInfoImage("ListItem.Thumb")
    plot = unicode(xbmc.getInfoLabel("ListItem.Plot"), "utf-8")
    director = unicode(xbmc.getInfoLabel("ListItem.Director"), "utf-8")
    date = unicode(xbmc.getInfoLabel("ListItem.Date"), "utf-8")
    year = unicode(xbmc.getInfoLabel("ListItem.Year"), "utf-8")
    studio = unicode(xbmc.getInfoLabel("ListItem.Studio"), "utf-8")
    # Parse HTML results page...
    html = urllib.urlopen(self.Arguments('url')).read()
    # Get FLV video...
    match = re.compile('so.addVariable\(\'file\'\,\'(.+?)\'\)\;').findall(html)
    for _url in match:
      video_url = _url
    # Create video playlist...
    playlist = xbmc.PlayList(1)
    playlist.clear()
    # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
    listitem = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    # set the key information
    listitem.setInfo("Video", {"Title": title,
                               "Label" : title,
                               "Director" : director,
                               "Plot": plot,
                               "PlotOutline": plot,
                               "Date" : date,
                               #"Year" : year,
                               "Studio" : studio })
    # add item to our playlist
    playlist.add(video_url, listitem)
    # Play video...
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

  def convertTextToDate(self, date) :
    if not date:
      return "unknown date"

    parts = date.split(" ")
    month = parts[0]
    day = parts[1]
    year = parts[2]

    if parts[0] == "January": month = "01"
    if parts[0] == "February": month = "02"
    if parts[0] == "March": month = "03"
    if parts[0] == "April": month = "04"
    if parts[0] == "May": month = "05"
    if parts[0] == "June": month = "06"
    if parts[0] == "July": month = "07"
    if parts[0] == "August": month = "08"
    if parts[0] == "September": month = "09"
    if parts[0] == "October": month = "10"
    if parts[0] == "November": month = "11"
    if parts[0] == "December": month = "12"

    if parts[1] == "1": day = "01"
    if parts[1] == "2": day = "02"
    if parts[1] == "3": day = "03"
    if parts[1] == "4": day = "04"
    if parts[1] == "5": day = "05"
    if parts[1] == "6": day = "06"
    if parts[1] == "7": day = "07"
    if parts[1] == "8": day = "08"
    if parts[1] == "9": day = "09"

    _date = day + "." + month + "." + year
    _year = year

    return _date, _year

  def Arguments(self, arg):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(Arguments[arg])

  def LOG(self, description):
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

  def fetch(self, url, max_age=0):
    # Use MD5 hash of the URL as the filename
    print url
    filename = md5.new(url).hexdigest()
    filepath = os.path.join(self.cache_dir, filename)
    if os.path.exists(filepath):
      if int(time.time()) - os.path.getmtime(filepath) < max_age:
        if Debug: print 'file exists and reading from cache.'
        return open(filepath).read()
    # Retrieve over HTTP and cache, using rename to avoid collisions
    if Debug: print 'file not yet cached or cache time expired. File reading from URL and try to cache to disk'
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
