from HTMLParser import HTMLParser
import os, sys, urllib2

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
  return curseParser.links

if __name__ == "__main__":
    all_addon_pages = [
      "http://www.curse.com/addons/wow/ace3/555250",                      # Ace3
      "http://www.curse.com/addons/wow/npcscan/555853",                   # _NPCScan
      "http://www.curse.com/addons/wow/npcscan-overlay/555852",           # _NPCScan.Overlay
      "http://www.curse.com/addons/wow/ark-inventory/555718",             # ArkInventory
      "http://www.curse.com/addons/wow/atlasloot-enhanced/555223",        # AtlasLoot Enhanced
      "http://www.curse.com/addons/wow/broker_equipment/531431",          # Broker_Equipment
      "http://www.curse.com/addons/wow/broker-portals/557793",            # Broker_Portal
      "http://www.curse.com/addons/wow/broker_recountfu/547068",          # Broker_RecountFu
      "http://www.curse.com/addons/wow/broker_sysmon/527030",             # Broker_SysMon
      "http://www.curse.com/addons/wow/chocolatebar/556665",              # Chcolatebar
      "http://www.curse.com/addons/wow/deadly-boss-mods/557298",          # DBM
      "http://www.curse.com/addons/wow/fizzle/556215",                    # Fizzle
      "http://www.curse.com/addons/wow/gathermate2/529390",               # GatherMate2
      "http://www.curse.com/addons/wow/gathermate2_data/555089",          # GatherMate2_Data
      "http://www.curse.com/addons/wow/grid2/556653",                     # Grid2
      "http://www.curse.com/addons/wow/inflight-taxi-timer/556048",       # InFlight
      "http://www.curse.com/addons/wow/jpack/551562",                     # JPack
      "http://www.curse.com/addons/wow/postal/529429",                    # Postal
      "http://www.curse.com/addons/wow/powerauras-classic/557951",        # PowerAuras
      "http://www.curse.com/addons/wow/mik-scrolling-battle-text/556071", # MikScrollingBattleText
      "http://www.curse.com/addons/wow/quartz/556504",                    # Quartz
      "http://www.curse.com/addons/wow/questhubber/555812",               # QuestHubber
      "http://www.curse.com/addons/wow/range-display/556323",             # RangeDisplay
      "http://www.curse.com/addons/wow/rating-buster/526602",             # RatingBuster
      "http://www.curse.com/addons/wow/recount/555916",                   # Recount
      "http://www.curse.com/addons/wow/silver-dragon/555791",             # SilverDragon
      "http://www.curse.com/addons/wow/spellflash/556290",                # SpellFlash
      "http://www.curse.com/addons/wow/xperl/555513",                     # X-Perl UnitFrame
      "http://www.curse.com/addons/wow/coordinates/557325",               # Coordinates
      "http://www.curse.com/addons/wow/inspect-equip/526511",             # InspectEquip
      "http://www.curse.com/addons/wow/tradeskill-info/502280",           # TradeSkillInfo
      "http://www.curse.com/addons/wow/vendomatic/558093",                # Vend-o-matic
    ]
    
    addational_links = [
      "http://fizzwidget.com/downloads/gfw-factionfriend-4-3.zip"         # FactionFriend
    ]
    
    links = []
    print("Parseing all links...")
    for addon_page in all_addon_pages:
      links += get_download_links(addon_page)
    links += addational_links
    
    for link in links:
      print("Downloading from %s ..." % (link))
      download_file(link, os.getcwd())
    print("ALL DONE!")
