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

def get_package_core(name, id , fetcher):
    message = "DONE!"
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
        return -1, "FAILED, %s" % (str(e),)
    return None, message

def new_task(name, id, fetcher):
    def _task_core():
      return get_package_core(name, id, fetcher)
    _task_core.name = name
    _task_core.id = id
    _task_core.fetcher = fetcher
    return _task_core

def load_configuration(config_file):
  import json
  data = file(config_file).read()
  
  try:
    return json.loads(data)
  except ValueError as e:
    report_info("Invalid configuration file '%s', %s" % (config_file, e.message))
    exit(EX_INVALID_JSON)

def get_tasks():
    tasks = []
    data = load_configuration("addons.json")
    for k in data:
        group = k
        addons = data[k]
        fetcher = globals()["get_%s_download_info" % (group)]
        for name in addons:
            tasks.append(new_task(name, addons[name], fetcher))
    return tasks

class TaskManager(object):
  import threading
  lock = threading.Lock()
  
  def run(self, tasks):
    import time
    from Queue import Queue
    from threading import Thread

    def _job_core(tasks):
      while tasks.qsize() > 0:
        if self.lock.acquire():
          task = tasks.get()
          self.lock.release()
          code, msg  = task()
          log(">> [%s] : %s" % (task.name, msg))
          if isinstance(code, int): exit(code)
          if tasks.qsize() != 0:
              log("   Reaming %d." % (tasks.qsize()))
          tasks.task_done()
    
    JOBS_SIZE = 5
    runningTasks = Queue()
    # Run tasks with job size
    for task in tasks:
        runningTasks.put(task)
    
    runners = []
    for i in xrange(JOBS_SIZE):
        runner = Thread(target = _job_core, args = (runningTasks,))
        runner.daemon = True
        runner.start()
        runners.append(runner)
    # Wait all tasks complete, It can response Ctrl + C interrupt.
    while any(runner.isAlive() for runner in runners):
      time.sleep(1)
    runningTasks.join()


if __name__ == "__main__":
    taskMan = TaskManager()
    taskMan.run(get_tasks())
    
    log("ALL DONE!")
