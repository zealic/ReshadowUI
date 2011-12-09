from HTMLParser import HTMLParser
import os, sys, urllib2
import threading, time

def log(msg):
  sys.stdout.write("%s\n" % (msg))

class CurseDownloadPageHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.links = []

  def handle_starttag(self, tag, attrs):
    #print "Encountered the beginning of a %s tag" % tag
    if tag == "a":
      if len(attrs) == 0: pass
      else:
        for (variable, value)  in attrs:
          if variable == "data-href":
            self.links.append(value)

def fetch_http_proxy():
  if os.environ.has_key("HTTP_PROXY"):
      proxy_support = urllib2.ProxyHandler({'http': os.environ["HTTP_PROXY"]})
      opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
      urllib2.install_opener(opener)

def download_file(url, dir):
  BUFFER_SIZE = 4096
  base_name = os.path.basename(url)
  if not os.path.exists(dir):
    os.makedirs(dir)

  file_path = os.path.join(dir, base_name)

  re = urllib2.Request(url)
  target_file = file(file_path, 'wb')
  try:
    fd = urllib2.urlopen(re)
    while True:
      rs = fd.read(BUFFER_SIZE)
      if rs == "":
        break
      target_file.write(rs)
  except:
    target_file.close()
    os.remove(file_path)
    raise
  finally:
    if not target_file.closed: target_file.close()

def get_download_links(url):
  req = urllib2.Request(url)  
  response = urllib2.urlopen(req)
  html = response.read()
  curseParser = CurseDownloadPageHTMLParser()
  curseParser.feed(html)
  curseParser.close()
  return (len(curseParser.links) > 0 and curseParser.links or [None])[0]

def get_package_core(notifier, download_link, link_is_curse_name):
  result = "[%s] DONE!" % (notifier.name)
  try:
    if link_is_curse_name == True:
      curse_page = "http://www.curse.com/addons/wow/%s/download" % (download_link)
      log("[%s] Fetching addon '%s' download link..." % (notifier.name, curse_page))
      download_link = get_download_links(curse_page)
    if download_link == None:
      log("[%s] No download link!" % (notifier.name))
    else:
      log("[%s] Downloading '%s' ..." % (notifier.name, download_link))
      download_file(download_link, os.getcwd())
  except Exception, e:
    result = "[%s] FAILED, %s" % (notifier.name, str(e))
  notifier.message = result
  notifier.set()

def async_get_package(download_link, link_is_curse_name):
  notifier = threading.Event()
  notifier.name = download_link
  runner = threading.Thread(target=get_package_core, args = (notifier, download_link, link_is_curse_name))
  runner.name = download_link
  runner.start()
  return notifier

if __name__ == "__main__":
    curse_addon_names = [
      "ace3",                      # Ace3
      "npcscan",                   # _NPCScan
      "npcscan-overlay",           # _NPCScan.Overlay
      "ark-inventory",             # ArkInventory
      "atlasloot-enhanced",        # AtlasLoot Enhanced
      "broker_equipment",          # Broker_Equipment
      "broker-portals",            # Broker_Portal
      "broker_recountfu",          # Broker_RecountFu
      "broker_sysmon",             # Broker_SysMon
      "chocolatebar",              # Chcolatebar
      "deadly-boss-mods",          # DBM
      "fizzle",                    # Fizzle
      "gathermate2",               # GatherMate2
      "gathermate2_data",          # GatherMate2_Data
      "grid2",                     # Grid2
      "inflight-taxi-timer",       # InFlight
      "jpack",                     # JPack
      "postal",                    # Postal
      "powerauras-classic",        # PowerAuras
      "mik-scrolling-battle-text", # MikScrollingBattleText
      "quartz",                    # Quartz
      "questhubber",               # QuestHubber
      "range-display",             # RangeDisplay
      "rating-buster",             # RatingBuster
      "recount",                   # Recount
      "silver-dragon",             # SilverDragon
      "spellflash",                # SpellFlash
      "xperl",                     # X-Perl UnitFrame
      "coordinates",               # Coordinates
      "inspect-equip",             # InspectEquip
      "tradeskill-info",           # TradeSkillInfo
      "vendomatic",                # Vend-o-matic
    ]
    
    addational_links = [
      "http://fizzwidget.com/downloads/gfw-factionfriend-4-3.zip"         # FactionFriend
    ]
    
    notifiers = []
    for i in xrange(0, len(curse_addon_names)):
      notifiers.append(async_get_package(curse_addon_names[i], True))
    for i in xrange(0, len(addational_links)):
      notifiers.append(async_get_package(addational_links[i], False))
    
    taskCount = len(notifiers)
    while len(notifiers) != 0:
        finishedTask = None
        for notifier in notifiers:
          notifier.wait(0)
          if notifier.is_set():
            finishedTask = notifier
            break;
        if finishedTask != None:
          notifiers.remove(finishedTask)
          log(">> %d/%d : %s" %(taskCount - len(notifiers), taskCount, finishedTask.message))
        time.sleep(0.05)
    log("ALL DONE!")
