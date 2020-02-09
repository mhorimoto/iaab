TARGD=/usr/local/bin
CFGFD=/etc/uecs
PYLIBD=/usr/local/lib/python3.6/dist-packages
SYSTMD=/etc/systemd/system
NTPDC=/etc/ntp.conf

EXECP=$(TARGD)/iaab.py
SCANP=$(TARGD)/scanresponse.py
SYSCD=$(SYSTMD)/iaab.service
BYECD=$(SYSTMD)/bye.service
SCAND=$(SYSTMD)/scanresponse.service
PYUECS=$(PYLIBD)/PyUECS.py
CONFF=$(CFGFD)/config.ini
XMLFF=$(CFGFD)/iaab.xml
BYEP=$(TARGD)/bye.sh

$(PYUECS): PyUECS.py
	cp $^ $(PYLIBD)

$(EXECP): iaab.py
	install $^ $(TARGD)

$(BYEP): bye.sh
	install $^ $(TARGD)

$(SCANP): scanresponse.py
	install $^ $(TARGD)

$(CONFF): config.ini
	cp $^ $(CONFF)

$(XMLFF): iaab.xml
	cp $^ $(XMLFF)

$(SYSCD): iaab.service
	cp $^ $(SYSCD)

$(BYECD): bye.service
	cp $^ $(BYECD)

$(SCAND): scanresponse.service
	cp $^ $(SCAND)

$(NTPDC): ntp.conf
	@mv $(NTPDC) $(NTPDC)-orig
	cp $^ $(NTPDC)

install: $(EXECP) $(SCANP) $(CONFF) $(XMLFF) $(SYSCD) $(SCAND) $(NTPDC) $(BYEP) $(BYECD)


