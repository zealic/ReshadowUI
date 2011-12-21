# -*- coding: utf-8 -*-
import os, sys, urllib2
import threading, time
sys.path.append(os.path.join(sys.path[0], "Lib"))
from ReshadowUI import *

def get_general_download_info(name, id):
    url = id
    req = urllib2.Request(url)  
    response = urllib2.urlopen(req)
    headers = response.info()
    result = parse_headers(headers)
    result.link = id
    return result

def get_curse_download_info(name, id):
    from BeautifulSoup import BeautifulSoup
    url = "http://www.curse.com/addons/wow/%s/download" % (id)
    req = urllib2.Request(url)  
    response = urllib2.urlopen(req)
    html = response.read()
    response.close()
    soup = BeautifulSoup(html)
    link = soup.find("a", {"class":"download-link"})["data-href"]
    if link:
        req = urllib2.Request(link)  
        response = urllib2.urlopen(req)
        headers = response.info()
        result = parse_headers(headers)
        result.link = link
        return result
    return None

def get_wowinterface_download_info(name, id):
    url = "http://www.wowinterface.com/downloads/download%s" % (id)
    req = urllib2.Request(url)  
    response = urllib2.urlopen(req)
    headers = response.info()
    result = parse_headers(headers)
    result.link = url
    return result

def get_package_core(task, name, id, fetcher):
    task.message = "[%s] DONE!" % (name)
    try:
        log("[%s] Fetching '%s' download info..." % (name, id))
        info = fetcher(name, id)
        download_link = info.link
        base_name = None
        if info.attachment:
            base_name = info.attachment.name
        if download_link == None:
            log("[%s] No download link!" % (name))
        else:
            log("[%s] Downloading '%s' ..." % (name, download_link))
            download_file(download_link, os.getcwd(), base_name)
    except Exception, e:
        task.message = "[%s] FAILED, %s" % (name, str(e))
    task.event.set()

def new_task(name, id, fetcher):
    from StringIO import StringIO
    task = StringIO()
    task.event = threading.Event()
    task.runner = threading.Thread(target=get_package_core, args = (task, name, id, fetcher))
    task.runner.name = name
    task.runner.start()
    return task

if __name__ == "__main__":
    general_addons = {
      "FactionFriend"             : "http://fizzwidget.com/downloads/gfw-factionfriend-4-3.zip"
    }
    
    wowinterface_addons = {
      "OmoniCC"                   : "4836",
      "WitchHunt"                 : "8513",
    }

    curse_addons = {
      "Ace3"                      : "ace3",
      "_NPCScan"                  : "npcscan",
      "_NPCScan.Overlay"          : "npcscan-overlay",
      "ArkInventory"              : "ark-inventory",
      "AtlasLoot Enhanced"        : "atlasloot-enhanced",
      "Broker_Equipment"          : "broker_equipment",
      "Broker_Portal"             : "broker-portals",
      "Broker_RecountFu"          : "broker_recountfu",
      "Broker_SysMon"             : "broker_sysmon",
      "Chcolatebar"               : "chocolatebar",
      "DBM"                       : "deadly-boss-mods",
      "Fizzle"                    : "fizzle",
      "GatherMate2"               : "gathermate2",
      "GatherMate2_Data"          : "gathermate2_data",
      "Grid2"                     : "grid2",
      "InFlight"                  : "inflight-taxi-timer",
      "JPack"                     : "jpack",
      "Postal"                    : "postal",
      "PowerAuras"                : "powerauras-classic",
      "MikScrollingBattleText"    : "mik-scrolling-battle-text",
      "Quartz"                    : "quartz",
      "QuestHubber"               : "questhubber",
      "RangeColors"               : "rangecolors",
      "RangeDisplay"              : "range-display",
      "RatingBuster"              : "rating-buster",
      "Recount"                   : "recount",
      "ReforgeLite"               : "reforgelite",
      "SilverDragon"              : "silver-dragon",
      "Snoopy Inspect"            : "snoopy-inspect", # 超出距离依然能查看
      "TellMeWhen"                : "tellmewhen",
      "X-Perl UnitFrame"          : "xperl",
      "Coordinates"               : "coordinates",
      "InspectEquip"              : "inspect-equip",
      "TradeSkillInfo"            : "tradeskill-info",
      "Vend-o-matic"              : "vendomatic",
    }
    
    tasks = []
    for k in general_addons:
        tasks.append(new_task(k, general_addons[k], get_general_download_info))
    for k in wowinterface_addons:
        tasks.append(new_task(k, wowinterface_addons[k], get_wowinterface_download_info))
    for k in curse_addons:
        tasks.append(new_task(k, curse_addons[k], get_curse_download_info))
    
    taskCount = len(tasks)
    while len(tasks) != 0:
        finishedTask = None
        for task in tasks:
            task.event.wait(0)
            if task.event.is_set():
                finishedTask = task
                break;
        if finishedTask != None:
            tasks.remove(finishedTask)
            log(">> %d/%d : %s" %(taskCount - len(tasks), taskCount, finishedTask.message))
        time.sleep(0.05)
    log("ALL DONE!")
