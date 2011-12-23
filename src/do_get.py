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

def get_package_core(task):
    message = "[%s] DONE!" % (task.name)
    try:
        log("[%s] Fetching '%s' download info..." % (task.name, task.id))
        info = task.fetcher(task.name, task.id)
        download_link = info.link
        base_name = None
        if info.attachment:
            base_name = info.attachment.name
        if download_link == None:
            log("[%s] No download link!" % (task.name))
        else:
            log("[%s] Downloading '%s' ..." % (task.name, download_link))
            download_file(download_link, os.getcwd(), base_name)
    except Exception, e:
        message = "[%s] FAILED, %s" % (task.name, str(e))
    return message

def new_task(name, id, fetcher):
    from StringIO import StringIO
    task = StringIO()
    task.name = name
    task.id = id
    task.fetcher = fetcher
    return task

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

def job_core(tasks):
    while tasks.qsize() > 0:
        task = tasks.get()
        msg  = get_package_core(task)
        log(">> [%s] : %s" % (task.name, msg))
        if tasks.qsize() != 0:
            log("   Reaming %d." % (tasks.qsize()))
        tasks.task_done()

def start_jobs(tasks):
    JOBS_SIZE = 5
    from threading import Thread
    for i in xrange(1, JOBS_SIZE):
        runner = Thread(target=job_core, args = (tasks,))
        runner.start()

if __name__ == "__main__":
    from Queue import Queue
    runningTasks = Queue()
    for task in get_tasks():
        runningTasks.put(task)
    
    start_jobs(runningTasks)
    runningTasks.join()
    
    log("ALL DONE!")
