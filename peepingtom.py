import sys
import socket
import urllib2
import subprocess
import re
import time
import os
from urlparse import urlparse

#=================================================
# MAIN FUNCTION
#=================================================

def main():
    import optparse
    usage = "%prog [options]\n\n%prog - Tim Tomes (@LaNMaSteR53) (www.lanmaster53.com)"
    parser = optparse.OptionParser(usage=usage, version="%prog 1.2")
    parser.add_option('-v', help='Enable verbose mode.', dest='verbose', default=False, action='store_true')
    parser.add_option('-i', help='File input mode. Name of input file. [IP:PORT]', dest='infile', type='string', action='store')
    parser.add_option('-u', help='Single URL input mode. URL as a string.', dest='url', type='string', action='store')
    parser.add_option('-q', help='PyQt4 capture mode. PyQt4 python modules required.', dest='pyqt', default=False, action='store_true')
    parser.add_option('-p', help='Phantonjs capture mode. Phantomjs required.', dest='phantom', default=False, action='store_true')
    (opts, args) = parser.parse_args()

    if not opts.infile and not opts.url:
        parser.error("[!] Must provide input. Mode option required.")
    if not opts.pyqt and not opts.phantom:
        capture = False
        print '[!] WARNING: No capture mode provided. Retrieving header data only.'
    else:
        capture = True
    if opts.infile:
        targets = open(opts.infile).read().split()
    if opts.url:
        targets = []
        targets.append(opts.url)

    dir = time.strftime('%y%m%d_%H%M%S', time.localtime())
    print '[*] Storing data in \'%s/\'' % (dir)
    os.mkdir(dir)
    outfile = '%s/report.html' % (dir)
    
    socket.setdefaulttimeout(5)

    zombies = []
    servers = {}
    # logic for validating list of urls and building a new list which understands the redirected sites.
    try:
        for target in targets:
            headers = None
            prefix = ''
            # best guess at protocol prefix
            if not target.startswith('http'):
                if target.find(':') == -1: target += ':80'
                prefix = 'http://'
                if target.split(':')[1].find('443') != -1:
                    prefix = 'https://'
            # drop port suffix where not needed
            if target.endswith(':80'): target = ':'.join(target.split(':')[:-1])
            if target.endswith(':443'): target = ':'.join(target.split(':')[:-1])
            # build legitimate target url
            target = prefix + target
            code, headers = getHeaderData(target)
            if code == 'zombie':
                zombies.append((target, headers))
            else:
                filename = '%s.png' % re.sub('\W','',target)
                servers[target] = [code, filename, headers]
                if capture: getCapture(code, target, '%s/%s' % (dir,filename), opts)
    except KeyboardInterrupt:
        print ''
    
    generatePage(servers, zombies, outfile)
    print 'Done.'

#=================================================
# SUPPORT FUNCTIONS
#=================================================

def getCapture(code, url, filename, opts):
    if code != 401:
        verbose = opts.verbose
        try:
            if opts.pyqt:      cmd = 'python ./capture.py %s %s' % (url, filename)
            elif opts.phantom: cmd = './phantomjs --ignore-ssl-errors=yes ./capture.js %s %s' % (url, filename)
            else: return
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            stdout, stderr = proc.communicate()
            response = str(stdout) + str(stderr)
            returncode = proc.returncode
            if returncode != 0:
                print '[!] %d: %s' % (returncode, response)
            if response != 'None':
                if verbose: print '[+] \'%s\' => %s' % (cmd, repr(response))
        except KeyboardInterrupt:
            pass

def getHeaderData(target):
    server = None
    url = None
    code = None
    status = None
    headers = None
    header_str = None
    server = urlparse(target)
    # set up request for getting header information
    opener = urllib2.build_opener(SmartRedirectHandler) # debug with urllib2.HTTPHandler(debuglevel=1)
    urllib2.install_opener(opener)
    req = urllib2.Request(server.geturl())
    try:
        res = urllib2.urlopen(req)#,'',3)
        print '[*] %s %s. Good.' % (target, res.getcode())
    except Exception as res:
        try:
            res.getcode()
            print '[*] %s %s. Good.' % (target, res.getcode())
        except:
            error = res.__str__()
            print '[*] %s %s. Visit manually from report.' % (target, error)
            return 'zombie', error

    url = res.geturl()
    code = res.code
    status = res.msg
    headers = res.info().headers       
    header_str = '<br />%s %s<br />\n' % (code, status)
    for header in headers:
        header_str += '<span class="header">%s</span>: %s<br />\n' % (header.split(':')[0].strip(), header.split(':')[1].strip())
    return code, header_str

def generatePage(servers, zombies, outfile):
    tmarkup = ''
    zmarkup = ''
    for server in servers.keys():
        tmarkup += "<tr>\n<td class='img'><img src='%s' /></td>\n<td class='head'><a href='%s' target='_blank'>%s</a> %s</td>\n</tr>\n" % (servers[server][1],server,server,servers[server][2])
    if len(zombies) > 0:
      zmarkup = '<tr><td><h2>Failed Requests</h2></td><td>\n'
      for server in zombies:
          zmarkup +=  "<a href='%s' target='_blank'>%s</a> %s<br />\n" % (server[0],server[0],server[1])
      zmarkup += '</td></tr>\n'
    file = open(outfile, 'w')
    file.write("""
<!doctype html>
<head>
<style>
table, td, th {border: 1px solid black;border-collapse: collapse;padding: 5px;font-size: .9em;font-family: tahoma;}
table {table-layout:fixed;}
td.img {width: 400px;white-space: nowrap;}
td.head {vertical-align: top;word-wrap:break-word;}
.header {font-weight: bold;}
img {width: 400px;}
</style>
</head>
<body>
<table width='100%%'>
%s%s
</table>
</body>
</html>""" % (tmarkup, zmarkup))
    file.close()

#=================================================
# CUSTOM CLASS WRAPPERS
#=================================================

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        result.msg = msg + ' (Redirect)'
        return result
    http_error_302 = http_error_303 = http_error_307 = http_error_301

#=================================================
# START
#=================================================

if __name__ == "__main__": main()
