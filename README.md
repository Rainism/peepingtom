##Screen Capturing with Peepingtom

Solving the problem of managing large quantities of web servers discovered by Nmap scans.

The traditional approach is to open up each of the servers in a browser to see what’s there, then make a decision on which servers to attack, if any. This is highly inefficient, and in the case of a time constrained penetration test, not practical.

Peepingtom will quickly organize your nmap results with screenshots of each server page so you can quickly scan through and see which servers look best for exploitation.


##STEPS:

First you will need to put the banner-plus.nse file inside your scripts folder for nmap (/usr/share/nmap/scripts/).

The peepingtom folder will be located inside the /opt directory.

Using nmap, you will output your results to the /opt/peepingtom/ directory using a file name that suites your report.
(e.g. /opt/peepingtom/report<IP CIDR> )

Example:
nmap --script /usr/share/nmap/scripts/banner-plus.nse --min-rate=400 --min-parallelism=256 -p 1-65535 -n -Pn -PS -oA /opt/peepingtom/report<IP CIDR>

*Switch List*
--script = location of banner-plus.nse script
--min-rates = guarantee that scan will be finished by time (secs)
--min-parallelism = speed up total number of probes
-p = ports to scan
-n = disable DNS resolution (speeds up scan)
-Pn = disable ping (speeds up scan)
-PS = TCP SYN Ping
-oA = export in the three major formats at once

Before kicking off peepingtom we need to prep & clean the data for scraping. Gnmap.pl is a perl script that will take the results and clean it to a list of IP addresses.

Example:
cd /opt/peepingtom

cat report.gnmap | ./gnmap.pl | grep http | cut -f 1,2 -d "," | tr "," ":" > http_ips.txt

python ./peepingtom.py -p -i http_ips.txt

A new folder will be created and named based on a date timestamp in the peepingtom folder. Open report.html in a browser.

### Notes

- Input is limited only to what PhantomJS allows. PhantomJS will take any string as input for the location of a resource. If a protocol is not given, PhantomJS assumes the string is a file path on the local operating system. Ports apply as normal.
- Pages which use JavaScript to redirect the browser will show up as a blank screen shot in the report and the standard `200 OK` response headers will be displayed.
- The TCP timeout can be adjusted within the setTimeout method call inside `capture.js`.

