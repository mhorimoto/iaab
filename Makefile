TARGD=/usr/local/bin
CFGFD=/etc/uecs
PYLIBD=/usr/local/lib/python3.6/dist-packages
SYSTMD=/etc/systemd/system
NTPDC=/etc/ntp.conf

EXECP=$(TARGD)/todtalkerd.py
SCANP=$(TARGD)/scanresponse.py
SYSCD=$(SYSTMD)/todtalker.service
SCAND=$(SYSTMD)/scanresponse.service
PYUECS=$(PYLIBD)/PyUECS.py
CONFF=$(CFGFD)/config.ini
XMLFF=$(CFGFD)/todtalker.xml


$(PYUECS): PyUECS.py
	cp $^ $(PYLIBD)

$(EXECP): todtalkerd.py
	install $^ $(TARGD)

$(SCANP): scanresponse.py
	install $^ $(TARGD)

$(CONFF): config.ini
	cp $^ $(CONFF)

$(XMLFF): todtalker.xml
	cp $^ $(XMLFF)

$(SYSCD): todtalker.service
	cp $^ $(SYSCD)

$(SCAND): scanresponse.service
	cp $^ $(SCAND)

$(NTPDC): ntp.conf
	@mv $(NTPDC) $(NTPDC)-orig
	cp $^ $(NTPDC)

install: $(EXECP) $(SCANP) $(CONFF) $(XMLFF) $(SYSCD) $(SCAND) $(NTPDC)


