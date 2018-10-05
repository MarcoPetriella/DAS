# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 21:04:58 2018

@author: Marco
"""

import numpy
import matplotlib.pyplot as plot
import sys
import visa

rm = visa.ResourceManager()
# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
instruments = rm.list_resources()
usb = list(filter(lambda x: 'USB' in x, instruments))
if len(usb) != 1:
    print('Bad instrument list', instruments)
    sys.exit(-1)
    
power_supply = rm.open_resource(usb[0], timeout=20, chunk_size=1024000)



power_supply.write(":APPL CH2,2.25,0.1")

query = power_supply.query(":APPL? CH2")
print query

power_supply.close()
