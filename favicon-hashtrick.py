#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

# Reference: https://twitter.com/noneprivacy/status/1177629325266505728

import re
import sys
import requests
import base64
import mmh3
import argparse
from shodan import Shodan
from colored import fg, bg, attr


def faviconHash( data, web ):
	if web:
		b64data = base64.encodebytes(data).decode()
	else:
		b64data = base64.encodebytes(data)
	
	b64data = base64.encodebytes(data).decode()
	return mmh3.hash(b64data)


parser = argparse.ArgumentParser()
parser.add_argument( "-b","--favfile64",help="favicon source file (base64 format)" )
parser.add_argument( "-f","--favfile",help="favicon source file" )
parser.add_argument( "-u","--favurl",help="favicon source url" )
parser.add_argument( "-k","--shokey",help="Shodan API key" )
parser.add_argument( "-v","--values",help="values you want separated by comma, default: ip	_str, can by: ip_str,http,data,domains,hash,ssl,timestamp,asn,_shodan,transport,os,isp,port,org,ip,tags,hostnames,location" )
parser.add_argument( "-s","--silent",help="silent mode, only results displayed", action="store_true" )

parser.parse_args()
args = parser.parse_args()

if args.values:
	t_values = args.values.split(',')
else:
	t_values = ['ip_str']

if args.shokey:
	shokey = args.shokey
else:
	shokey = False

if args.favfile64:
	favsource = args.favfile64
	data = open(favsource).read()
	data = data.replace( "\n", '' )
	data = re.sub( 'data:.*;base64,', '', data )
	data = base64.b64decode( data )
	web_src = False

if args.favfile:
	favsource = args.favfile
	data = open(favsource,'rb').read()
	web_src = False

if args.favurl:
	favsource = args.favurl
	r = requests.get( favsource )
	data = r.content
	web_src = True

if not args.favfile64 and not args.favfile and not args.favurl:
	parser.error( 'missing favicon' )

if not args.silent:
	sys.stdout.write( '%s[+] load favicon source: %s%s\n' % (fg('green'),favsource,attr(0)) )
	sys.stdout.write( '[+] favicon size: %d\n' % len(data) )

if not len(data):
	if not args.silent:
		sys.stdout.write( '%s[-] invalid favicon%s\n' % (fg('red'),attr(0)) )
	exit()

favhash = faviconHash( data, web_src )
if not args.silent:
	sys.stdout.write( '%s[+] hash calculated: %s%s\n' % (fg('green'),str(favhash),attr(0)) )

if shokey:
	shodan = Shodan( shokey )
	search = 'http.favicon.hash:' + str(favhash)
	if not args.silent:
		sys.stdout.write( '[+] searching: %s\n' % search )
	try:
		t_results = shodan.search( search )
		# print(t_results)
	except Exception as e:
		sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
		exit()
	if not args.silent:
		sys.stdout.write( '%s[+] %d results found%s\n' % (fg('green'),len(t_results['matches']),attr(0)) )
	for result in t_results['matches']:
		tmp = []
		for v in t_values:
			if v in result:
				tmp.append( str(result[v]) )
			else:
				tmp.append( '' )
		# print( tmp )
		sys.stdout.write( "%s\n" % ' - '.join(tmp) )

