#!/usr/bin/env python
"""
An animated image
"""
import win32pipe, win32file,time,struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing import Process
import sys

fileHandle = win32file.CreateFile("\\\\.\\pipe\\PipeFFT",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)
               
#tam=int(sys.argv[1])

#bin1=2000
#shots_per_chunk=5000
#total_chan=1

bin1=int(sys.argv[1])
shots_per_chunk=int(sys.argv[2])

filas = int(1+shots_per_chunk/2)



fig = plt.figure()
ax = fig.add_axes([.1,.1,.8,.72]) 


print 'HOLA'
data=np.zeros((filas,bin1))

im = plt.imshow(data, cmap=plt.get_cmap('jet'),aspect='auto')
#im.set_clim([0,10])
plt.colorbar()

i = 0;

def updatefig2(*args):
    global i
    i = i+1;
#    global data, fileHandle
#    f=(args[0])       
    rr,rd = win32file.ReadFile(fileHandle, filas*bin1*4) #2 es tamanio de datos

#    if (f>0 and (f)%60==0 ):
#        data=np.zeros((60,tam))
#        data[f%60]=np.frombuffer(rd,dtype=np.float32)
#    else:       
#        data[f%60]=np.frombuffer(rd,dtype=np.float32)       
    data1 = np.reshape(np.frombuffer(rd,dtype=np.float32) ,(bin1,filas))
    data1 = np.transpose(data1)
 
    im.set_array(data1)
    #im.set_clim([data1.min(),data1.max()])
    im.set_clim([float(0),float(2000000000)]) 
    ax.set_ylim([0,500])
    

    im.set_cmap('jet')
#    print data1.max(),data1.min()
    
    print i   
    return im,
    
ani = animation.FuncAnimation(fig, updatefig2, interval=4000, blit=False)
plt.show()