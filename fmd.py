#!/bin/python

import urllib, urllib2
import os, re
import zlib
import time
from datetime import datetime, timedelta

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)

PROJECT_STARTTAG = '<a style="cursor: pointer;text-align: left;vertical-align: middle;font-family: \'Arial\';font-size: 12px;color: #000000;background-color: normal;font-weight: bold;font-style:normal;text-decoration:none;font-variant:normal;letter-spacing: normal;text-transform: none;text-align: left;background-color: #EEEEEE;overflow: hidden;position: absolute;visibility: visible;top: 2px;left: 59px;width: 256px;height: 30px;" onkeypress="handleEvent(event);"'
PROJECT_STOPTAG = '">'

referer = 'http://www.9renproject.it/fmi/iwp/cgi?-db=9Ren_DB&-loadframes'

def header():
    print """fmd - FileMaker Downloader
Copyright (c) 2012 Gianpaolo Terranova <gianpaoloterranova@gmail.com>
All Rights Reserved.
"""
    
def usage(app, msg=''):
    print """Usage: %s <username> <password> <search terms>
%s""" % (app, msg)

def executebuttonscript(index, recid, relatedrecid):
    url = 'http://www.9renproject.it/fmi/iwp/cgi?-index=%s&-recid=%s&-relatedrecid=%s&-buttonscript=' % (index, recid, relatedrecid)

    data = _openUrl(url, headers={
        'Host':'www.9renproject.it',
        'Referer':referer,
        'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2)'})
    return data
    
def _openUrl(url, data=None, headers={}):    
    try:
        req = urllib2.Request(url, data, headers)  # create a request object
        handle = urllib2.urlopen(req)                     # and open it
    except IOError, e:
        print 'Failed to open "%s".' % url
        if hasattr(e, 'code'):
            print 'Error code: %s.' % e.code
    else:
        #print handle.headers
        #print '\n'
        #make sure the response is compressed
        isGZipped = handle.headers.get('content-encoding', '').find('gzip') >= 0
        data = handle.read()            
        if isGZipped:
            d = zlib.decompressobj(16+zlib.MAX_WBITS)
            data = d.decompress(data)
    return data
    
def extract(text, sub1, sub2):
    """extract a substring between two substrings sub1 and sub2 in text"""   
    ret = []
    a1 = text.split(sub1)
    if (len(a1)>1):
        for t1 in a1[1:]:
            a2 = t1.split(sub2)
            if len(a2)>1:
                ret.append(sub1 + a2[0] + sub2)
        return ret
    return []
                                      
def main(*args):
    import sys
    if sys.platform == "win32":
      from time import clock
    else:
      from time import time as clock

    header()
    if len(args)<3:
        usage(args[0], '\nArguments missing.\n')
        return

    username = args[1]
    password = args[2]

    if len(args)<4:
        usage(args[0], '\nArguments missing.')
        return
    
    progetto = " ".join(args[3:])
    
    start = clock()
    #params = {'-authdb':'','acct':'account','dbpath':'/fmi/iwp/cgi?-db=9Ren_DB&-loadframes','login':'Accesso','name':'gterranova','password':'italia2010'}

    params = 'dbpath=%2Ffmi%2Fiwp%2Fcgi%3F-db%3D9Ren_DB%26-loadframes&acct=account&name='+username+'&password='+password+'&login=Accesso&-authdb='
    data = _openUrl('http://www.9renproject.it/fmi/iwp/cgi?-authdb', data=params)

    data = _openUrl('http://www.9renproject.it/fmi/iwp/cgi?-open', headers={
        'Host':'www.9renproject.it',
        'Referer':'http://www.9renproject.it/fmi/iwp/cgi?-db=9Ren_DB&-loadframes',
        'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2)'})
    #print data

    projects_list = []
    for x in range(1,8):
        
        links = extract(data, '<a style="cursor: pointer;', '">')
        exec_re = re.compile('top.iwp.executebuttonscript\(([0-9]+),([0-9]+),([0-9]+)\)"')
        match = exec_re.search(links[0])
        prev_page = next_page = None
        if match:
            prev_page = match.groups()

        match = exec_re.search(links[1])
        if match:
            next_page = match.groups()


        projects = extract(data, PROJECT_STARTTAG, PROJECT_STOPTAG)
        compiled_re = re.compile('top.iwp.executebuttonscript\(([0-9]+),([0-9]+),([0-9]+)\)"  title="([A-Za-z0-9._ ]+)"')
        for prj in projects:
            match = compiled_re.search(prj)
            if match is not None:
                projects_list.append(match.groups())

        data = executebuttonscript(*next_page)

    found = False
    for prj in projects_list:
        if re.search(progetto.lower(), prj[3].lower()):
            found = True
            break
        
    if not found:
        print "Nessun progetto trovato."
        return
    
    print "\nSto scaricando il progetto %s..." % prj[3]

    try:
        os.mkdir(prj[3])
    except:
        pass
    try:
        os.chdir(prj[3])
    except:
        pass
    
    data = executebuttonscript(*prj[:-1])
    docs = ('171', prj[1], prj[2])

    data = executebuttonscript(*docs)
    #data = data.split('<div style="position: absolute;overflow: hidden;visibility: visible;left: -1px;top: 348px;height: 1px;width: 438px;border: none;background-color: #007700;">')
    cod = extract(data, '<span style="white-space: pre-wrap;cursor: default;">', '</span>')
    cod = [t[53:-7] for t in cod][3]

    titles = extract(data, '1px;"  title="', '">')
    docs = [(t[14:-2], 'http://62.149.193.94/9REN/files/Progetto_%s/%s' % (cod, urllib.quote(t[14:-2]))) for t in titles]

    for (doc, url) in docs:
        print "- %s" % doc
        data = _openUrl(url, headers={
        'Host':'www.9renproject.it',
        'Referer':'http://www.9renproject.it/fmi/iwp/cgi?-index=171&-recid=268&-relatedrecid=268&-buttonscript=',
        'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2)'})
        of = open(doc, 'wb')
        if data:
            of.write(data)
        of.close()
    
    print "\nExecution time: %f" % (clock() - start)
    
if __name__ == "__main__":
    import sys    
    main(*sys.argv)

    


    
