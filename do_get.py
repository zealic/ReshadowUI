# -*- coding: utf-8 -*-
import os, sys, urllib2
import threading, time
sys.path.append(os.path.join(os.getcwd(), "Lib"))
import Crawler

def log(msg):
    sys.stdout.write("%s\n" % (msg))

def get_curse_download_info(name, id):
    from BeautifulSoup import BeautifulSoup
    url = "https://www.curseforge.com/wow/addons/%s/download" % (id)
    html = Crawler.get_content(url)
    soup = BeautifulSoup(html)
    if soup == None:
        raise Exception("Cloud not fetch html, maybe anti by Cloudflare")
    link = soup.find("p", {"class":"text-sm"}).find("a")["href"]
    if not link:
        raise Exception("Can not found link")
    link = 'https://www.curseforge.com' + link
    response = Crawler.get(link, allow_redirects=False)
    result = type('', (), {})()
    result.link = response.url
    return result

def get_package_core(name, id , fetcher):
    message = "DONE!"
    try:
        log("[%s] Fetching '%s' download info..." % (name, id))
        info = fetcher(name, id)
        if info.link == None:
            log("[%s] No download link!" % (name))
        else:
            log("[%s] Downloading '%s' ..." % (name, info.link))
            download_file(info)
    except Exception, e:
        return -1, "FAILED, %s" % (str(e),)
    return None, message

def download_file(info):
    resp = Crawler.get(info.link)
    filename = os.path.basename(resp.url)
    file_path = os.path.join(os.getcwd(), filename)
    target_file = file(file_path, 'wb')
    try:
        target_file.write(resp.content)
    except:
        raise
    finally:
        if not target_file.closed: target_file.close()

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
    log("Invalid configuration file '%s', %s" % (config_file, e.message))
    exit(EX_INVALID_JSON)

def get_tasks():
    tasks = []
    data = load_configuration(sys.argv[1])
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
