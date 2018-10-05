#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 11:59:32 2017

@author: mvt
"""

import numpy as np
import win32file
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
import sys
import matplotlib.animation as ani

pipe = win32file.CreateFile("\\\\.\\pipe\\Pipe",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)    

def pipe2np(pipe,tam_data,data_type):
    
    err,data=win32file.ReadFile(pipe, tam_data)
    data=np.frombuffer(data,dtype=data_type)
    
    return data

def animacion_buffer(frame):
    global k,data
    for i in range (5):
        data[k,:]=pipe2np(pipe,bins*4,np.float32)
#        data[k,:]=np.random.normal(size=bins)
        k=((k+1)%max_k)
        im.set_clim([data.min(),data.max()])
    if k==5 :
        data[k:,:]=np.ones((max_k-k,bins))
        print 'llel'
    im.set_data(data)
    return im,
    
    
def init(*kwargs):
    global k,data
    k=0
    return im,
    
max_k=200
bins=int(sys.argv[1])
data=np.ones((max_k,bins))

fig,ax=plt.subplots()
im=ax.imshow(data,vmin=0,vmax=1,aspect='auto',interpolation='nearest',animated=True)

aa=ani.FuncAnimation(fig,func=animacion_buffer,init_func=init,interval=4000,blit=False)
plt.show()