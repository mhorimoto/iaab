#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

tree = ET.parse('todtalker.xml')
root = tree.getroot()
for ccm in root.findall('CCM'):
    detail = ccm.get('detail')
    exp = ccm.get('exp')
    print(exp,detail)

for cast in root.iter('cast'):
    print(cast.attrib)

