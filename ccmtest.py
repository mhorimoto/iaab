#! /usr/bin/python3
#coding: utf-8
import configparser
import xml.etree.ElementTree as ET

config = configparser.ConfigParser()
config.read('/etc/uecs/config.ini')

ccm = ET.parse(config['NODE']['xmlfile'])
ccmroot = ccm.getroot()

maxx = len(ccmroot)
maxy = int((maxx+1)/2)

cpag = 2
curx = int(cpag-1)*2 

print("CURX={0}".format(curx))
ccmt = ccmroot[curx]
print("CCM={0}".format(ccmt.text))
for cfgt in config[ccmt.text]:
    print("{0}={1}".format(cfgt,config[ccmt.text][cfgt]))
for ak in ccmt.attrib:
    print("{0}={1}".format(ak,ccmt.attrib[ak]))

curx+=1
if (curx < maxx):
    print("CURX={0}".format(curx))
    if (ccmroot[curx]!=""):
        ccmt = ccmroot[curx]
        print("CCM={0}".format(ccmt.text))
        for cfgt in config[ccmt.text]:
            print("{0}={1}".format(cfgt,config[ccmt.text][cfgt]))
        for ak in ccmt.attrib:
            print("{0}={1}".format(ak,ccmt.attrib[ak]))

    
