import os, sys, urllib2
from StringIO import StringIO

def __init__():
    __fetch_http_proxy()

def log(msg):
    sys.stdout.write("%s\n" % (msg))

def parse_headers(headers):
    import datetime
    result = StringIO()
    result.mime = headers.gettype()
    if headers.has_key("Last-Modified"):
        result.timestamp= datetime.datetime.strptime("Wed, 30 Nov 2011 01:43:34 GMT", "%a, %d %b %Y %H:%M:%S GMT")
    result.attachment = __parse_attachment(headers)
    return result

def download_file(url, dir, base_name = None):
    BUFFER_SIZE = 4096
    if base_name == None:
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

def __fetch_http_proxy():
    if os.environ.has_key("HTTP_PROXY"):
        proxy_support = urllib2.ProxyHandler({'http': os.environ["HTTP_PROXY"]})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

def __parse_attachment(headers):
    content_disposition = headers.get("Content-Disposition", None)
    
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        type = dispositions[0].lower()
        if bool(content_disposition and type):
            attachment = StringIO()
            attachment.content_type = headers.gettype()
            attachment.name = None
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None
            
            for param in dispositions[1:]:
                name,value = param.split("=")
                name = name.strip().lower()
                if name == "filename":
                    attachment.name = value.strip('"')
            return attachment
    return None
