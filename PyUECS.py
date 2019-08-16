#! /usr/bin/python3
#coding: utf-8
#
# Ver: 0.01
# Date: 2019/06/22
# Author: horimoto@holly-linux.com
#

import configparser
import xml.etree.ElementTree as ET
import netifaces
import uuid
from socket import *

class PyUECS:

    DATAPORT = 16520
    SCANPORT = 16529
    XML_HEADER  = "<?xml version=\"1.0\"?>"
    UECS_HEADER = "<UECS ver=\"1.00-E10\">"
    BUFFERSIZE  = 480
    CONFIGFILE  = "/etc/uecs/config.ini"
    
    def __init__(self,iface='eth0'):
        self.iface     = iface
        self.myipaddr  = netifaces.ifaddresses(self.iface)[netifaces.AF_INET][0]['addr']
        self.broadcast = netifaces.ifaddresses(self.iface)[netifaces.AF_INET][0]['broadcast']
        self.node = uuid.getnode()
        self.mac = uuid.UUID(int=self.node)
        self.macaddr = self.mac.hex[-12:].upper()
        self.scanaddr  = (self.broadcast,self.SCANPORT)
        # bind
        self.scanSock = socket(AF_INET, SOCK_DGRAM)
        self.scanSock.setsockopt(SOL_SOCKET,SO_REUSEADDR|SO_BROADCAST,1)
#        self.scanSock.bind(self.scanaddr) # HOST, PORTでbinding

        self.config = configparser.ConfigParser()
        self.config.read(self.CONFIGFILE)
        self.ccm = ET.parse(self.config['NODE']['xmlfile'])
        
    def dumpval(self):
        print("Interface={0}".format(self.iface))
        print("IP ADDRESS={0}".format(self.myipaddr))
        print("Broadcast={0}".format(self.broadcast))
        print("configfile={0}".format(self.CONFIGFILE))
        for cfgd in self.config['NODE']:
            print("  {0}={1}".format(cfgd,self.config['NODE'][cfgd]))

    def response_nodescan(self):
        cfgd  = self.config['NODE']
        sdata = "{0}{1}<NODE><NAME>{2}</NAME><VENDER>{3}</VENDER>"\
                "<UECSID>{4}</UECSID><IP>{5}</IP><MAC>{6}</MAC></UECS>".\
                format(self.XML_HEADER,self.UECS_HEADER,cfgd['name'],cfgd['vender'],\
                       cfgd['uecsid'],self.myipaddr,self.macaddr)
        self.scanSock.sendto(sdata.encode('utf-8'),self.scanaddr)

    def response_ccmscan(self,p=1):
        ccmroot = self.ccm.getroot()
        maxx    = len(ccmroot)
        maxy    = int((maxx+1)/2)
        cpag    = int(p)
        curx    = int(cpag-1)*2
        ccmt    = ccmroot[curx]
        ccmnum  = curx+1
        if (ccmnum < maxx):
            ccmcount = 2
        else:
            ccmcount = 1
        ccmtt   = self.config[ccmt.text]
        sdata = "{0}{1}<CCMNUM page=\"{2}\" total=\"{3}\">{4}</CCMNUM>"\
                "<CCM No=\"{5}\" room=\"{6}\" region=\"{7}\" order=\"{8}\" "\
                "priority=\"{9}\" cast=\"{10}\" unit=\"{11}\" SR=\"{12}\" "\
                "LV=\"{13}\">{14}</CCM>"\
                .format(self.XML_HEADER,self.UECS_HEADER,cpag,maxy,ccmcount,
                        ccmnum,ccmtt['room'],ccmtt['region'],ccmtt['order'],
                        ccmtt['priority'],ccmt.attrib['cast'],ccmt.attrib['unit'],ccmt.attrib['SR'],
                        ccmt.attrib['LV'],ccmt.text)
        curx   += 1
        ccmnum  = curx+1
        if (curx < maxx):
            if (ccmroot[curx]!=""):
                ccmt  = ccmroot[curx]
                ccmtt = self.config[ccmt.text]
                sdata += "<CCM No=\"{0}\" room=\"{1}\" region=\"{2}\" order=\"{3}\" "\
                         "priority=\"{4}\" cast=\"{5}\" unit=\"{6}\" SR=\"{7}\" "\
                         "LV=\"{8}\">{9}</CCM>"\
                         .format(ccmnum,ccmtt['room'],ccmtt['region'],ccmtt['order'],
                                 ccmtt['priority'],ccmt.attrib['cast'],ccmt.attrib['unit'],ccmt.attrib['SR'],
                                 ccmt.attrib['LV'],ccmt.text)
        sdata += "</UECS>"
        print(sdata)
        self.scanSock.sendto(sdata.encode('utf-8'),self.scanaddr)

    def send_cnd(self,ccmdata):
        ccmtype = ccmdata["type"]
        ccmval  = ccmdata["value"]
        ccmroot = self.ccm.getroot()
        cfgd    = self.config[ccmtype]
        for ccmrd in ccmroot:
            if (ccmrd.text==ccmtype):
                print("ccmrd={0}".format(ccmrd.text))
                sdata = "{0}{1}<DATA type=\"{2}\" root=\"{3}\" "\
                             "region=\"{4}\" order=\"{5}\" priority=\"{6}\">"\
                             "{7}</DATA><IP>{8}</IP></UECS>".\
                             format(self.XML_HEADER,self.UECS_HEADER,ccmtype,cfgd["room"],
                                    cfgd["region"],cfgd["order"],cfgd["priority"],
                                    ccmval,self.myipaddr)
                print(sdata)
                self.scanSock.sendto(sdata.encode('utf-8'),self.scanaddr)
#                for c0 in ccmrd.attrib:
#                    print("{0}={1}".format(c0,ccmrd.attrib[c0]))
#                for cfgt in cfgd:
#                    print("{0}={1}".format(cfgt,cfgd[cfgt]))
#                print("Value={0}".format(ccmdata["value"]))

                                    
if __name__ == '__main__':
    a = {
        "type" : "cnd.mXX",\
        "value": 67108864 }
    u = PyUECS()
#    u.dumpval()
    u.send_cnd(a)
    u.response_nodescan()
    u.response_ccmscan()
