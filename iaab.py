#! /usr/bin/python3
#coding: utf-8
#
# I Am Alive Beacon
# Version 2.40
# Date 2020/02/18
# Author M.Horimoto
#
import datetime
import time
import configparser
import netifaces
from socket import *
from subprocess import check_output,Popen
import signal

XML_HEADER  = "<?xml version=\"1.0\"?>"
UECS_HEADER = "<UECS ver=\"1.00-E10\">"
HOST = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
ADDRESS = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['broadcast']
PORT = 16520

def receive_shutdown(signum,stack):
    tn = "cnd.mXX"
    cndv = 134217728
    send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
        config[tn]['order'],config[tn]['priority'],cndv,HOST)
    quit()

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

prevmin = 0
prevsec = 0
ip      = HOST
lcdflag = False

config = configparser.ConfigParser()
config.read('/etc/uecs/config.ini')

if (config['NODE']['lcd_present']!='0'):
    import lcd_i2c as lcd
    lcd.lcd_init()
    lcdflag = True

##################################################
# Define signal handler
##################################################
signal.signal(signal.SIGRTMAX,receive_shutdown)
#signal.signal(signal.SIGKILL,receive_shutdown)
signal.signal(signal.SIGTERM,receive_shutdown)
signal.signal(signal.SIGHUP,receive_shutdown)

##################################################
# Initialize Completed
##################################################
tn = "cnd.mXX"
cndv = 67108864
send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
    config[tn]['order'],config[tn]['priority'],cndv,HOST)
time.sleep(1)
send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
    config[tn]['order'],config[tn]['priority'],cndv,HOST)



while(True):
    a=datetime.datetime.now()
    if (lcdflag):
        d="{0:2d}{1:02d}{2:02d}".format(a.year-2000,a.month,a.day)
        t=int("{0:2d}{1:02d}{2:02d}".format(a.hour,a.minute,a.second))
        s="{0:6s} {1:6d}".format(d,t)
        if (prevsec != a.second):
            l = lcd.LCD_LINE_2
            u = "U:{0}".format(s)
            lcd.lcd_string(u,l)
        l = lcd.LCD_LINE_1
        lcd.lcd_string(s,l)
        if (a.second>50):
            lcd.lcd_string(ip,lcd.LCD_LINE_2)
        elif (a.second>40):
            msg = "UECS IAAB.."
            lcd.lcd_string(msg,lcd.LCD_LINE_2)
        elif (a.second>30):
            lcd.lcd_string(ip,lcd.LCD_LINE_2)
        elif (a.second>20):
            msg = "UECS IAAB.."
            lcd.lcd_string(msg,lcd.LCD_LINE_2)
        elif (a.second>10):
            lcd.lcd_string(ip,lcd.LCD_LINE_2)

    time.sleep(0.1)
    if (prevmin != a.minute):
        cpute = 0   # CPU Read Error Flag
        ct = "/sys/class/thermal/thermal_zone0/temp"
        try:
            file = open(ct)
            cput0 = file.read().strip()
            cputf = float(cput0)/1000.0
        except Exception as e:
            cpute = 2097152
            if (lcdflag):
                lcd.lcd_string(e,lcd.LCD_LINE_2)
        finally:
            file.close()
        tn = "OPICPUTEMP.mXX"
        send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
                      config[tn]['order'],config[tn]['priority'],cputf,HOST)
        
    if (prevsec != a.second):
        tn = "cnd.mXX"
        pcmd = "ps ax | grep /usr/sbin/ntpd | grep -v grep | wc -l"
        ouv  = check_output(pcmd,shell=True)
        if (int(ouv)==0):
            cndv = cpute + 1048576 # No ntp daemon running
            pcmd = "systemctl restart ntp"
            popn = Popen(pcmd,shell=True)
        else:
            cndv = cpute + 0
        send_UECSdata(tn,config[tn]['room'],config[tn]['region'],\
                      config[tn]['order'],config[tn]['priority'],cndv,HOST)


    prevsec = a.second
    prevmin = a.minute
