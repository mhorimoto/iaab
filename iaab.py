#! /usr/bin/python3
#coding: utf-8
#
# TOD Talker
# Version 1.20
# Date 2019/06/25
# Author M.Horimoto
#
import lcd_i2c as lcd
import datetime
import time
import configparser
import netifaces
from socket import *
from subprocess import check_output,Popen

XML_HEADER  = "<?xml version=\"1.0\"?>"
UECS_HEADER = "<UECS ver=\"1.00-E10\">"
HOST = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
ADDRESS = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['broadcast']
PORT = 16520

def send_UECSdata(typename,room,region,order,priority,data,ip):
    s = socket(AF_INET,SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
    s.bind((HOST,PORT))
    ut = "{0}{1}<DATA type=\"{2}\" room=\"{3}\" region=\"{4}\" order=\"{5}\" "\
         "priority=\"{6}\">{7}</DATA><IP>{8}</IP></UECS>"\
         .format(XML_HEADER,UECS_HEADER,typename,room,region,order,priority,data,ip)
    s.sendto(ut.encode(),(ADDRESS,PORT))
    s.close()

###################################################

config = configparser.ConfigParser()
config.read('/etc/uecs/config.ini')

lcd.lcd_init()
prevsec = 0
itv     = 0
ip      = HOST

while(True):
    a=datetime.datetime.now()
    d="{0:2d}{1:02d}{2:02d}".format(a.year-2000,a.month,a.day)
    t=int("{0:2d}{1:02d}{2:02d}".format(a.hour,a.minute,a.second))
    s="{0:6s} {1:6d}".format(d,t)
    if (prevsec > a.second):
        l = lcd.LCD_LINE_2
        u = "U:{0}".format(s)
        lcd.lcd_string(u,l)
        tn = "Time"
        send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
                      config[tn]['order'],config[tn]['priority'],t,HOST)
        tn = "Date"
        send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
                      config[tn]['order'],config[tn]['priority'],d,HOST)
    l = lcd.LCD_LINE_1
    lcd.lcd_string(s,l)
    if (a.second>50):
        lcd.lcd_string(ip,lcd.LCD_LINE_2)
    elif (a.second>40):
        msg = "UECS todtalker.."
        lcd.lcd_string(msg,lcd.LCD_LINE_2)
    elif (a.second>30):
        lcd.lcd_string(ip,lcd.LCD_LINE_2)
    elif (a.second>20):
        msg = "UECS todtalker.."
        lcd.lcd_string(msg,lcd.LCD_LINE_2)
    elif (a.second>10):
        lcd.lcd_string(ip,lcd.LCD_LINE_2)
    prevsec = a.second
    time.sleep(0.01)
    itv += 1
    if (itv>=8):
        tn = "cnd.mXX"
        pcmd = "ps ax | grep /usr/sbin/ntpd | grep -v grep | wc -l"
        ouv  = check_output(pcmd,shell=True)
        if (int(ouv)==0):
            cndv = 1048576 # No ntp daemon running
            pcmd = "systemctl restart ntp"
            popn = Popen(pcmd,shell=True)
        else:
            cndv = 0
        send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
                      config[tn]['order'],config[tn]['priority'],cndv,HOST)
        itv = 0

