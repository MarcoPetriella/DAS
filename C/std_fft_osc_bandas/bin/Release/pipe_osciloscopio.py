# -*- coding: utf-8 -*-
"""
Created on Thu Oct 06 13:58:22 2016

@author: hh_s
"""

"""
A simple example of an animated plot
"""
import pandas as pd
import numpy as np
import win32pipe, win32file,time,struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import seaborn
import sys
import datetime 

print "pipe adentro"

fileHandle = win32file.CreateFile("\\\\.\\pipe\\Pipe3",
                              win32file.GENERIC_READ,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)

#tam=10000
bins=int(sys.argv[1])
cant_curvas=int(sys.argv[2])
qfrec=int(sys.argv[3])
tam = bins*cant_curvas*2


print "pipe adentro", tam

lines0 = []
lines1 = []

mvg_avg_window = 300

fig,([ax0,ax1]) = plt.subplots(2,1)

x0=np.random.uniform(0.05,0.1,size=(bins,1))
x00=np.random.uniform(0.05,0.1,size=(bins,1))
ax0 = plt.subplot2grid((2, 8), (0, 0), colspan=6)
for i in range(cant_curvas):
    lines0.append(ax0.plot(x0,color='b',linewidth=0.5,alpha=0.5))  
lines0.append(ax0.plot(x00,color='g',linewidth=1,alpha=1))     
lines0.append(ax0.plot(x00,color='k',linewidth=1,alpha=1))
    
ax0.grid(color='grey', linestyle='--', linewidth=0.5)
ax0.set_ylim([0,2])

ax0.set_title(u'CH0')
ax0.set_ylabel(u'Tensión [V]')
ax0.set_xlabel(u'Bin')

x1=np.random.uniform(0.05,0.1,size=(bins,1))
ax1 = plt.subplot2grid((2, 8), (1, 0), colspan=6)
for i in range(cant_curvas):
    lines1.append(ax1.plot(x1,color='r',linewidth=0.5,alpha=0.5))
ax1.grid(color='grey', linestyle='--', linewidth=0.5)
ax1.set_ylim([0,0.2])

ax1.set_title(u'CH1')
ax1.set_ylabel(u'Tensión [V]')
ax1.set_xlabel(u'Bin')


tiempo_actual = datetime.datetime.now()
time_str = datetime.datetime.strftime(tiempo_actual,'%Y-%m-%d %H:%M:%S')    
print time_str
#tiempo_label.set_text(time_str)
t0 = ax0.text(1.02,1.1,'T:' + str(time_str),horizontalalignment='left', transform=ax0.transAxes, color='k')   

rango1 = []
rango2 = []

def animate(i):
    #line.set_ydata(x+i/100.0)  # update the data
    #return line,
   # if(i%15==0 and i>0):
       
    global rango1, rango2   
    
    print 
  
    
#    ax.plot(x+i/10.0,'.')
    rr,rd = win32file.ReadFile(fileHandle,tam*4)
    datos = np.frombuffer(rd,dtype=np.float32)
    
    ch0 = datos[0:tam/2]
    ch1 = datos[tam/2:tam]
    
    ch0 = np.reshape(ch0,[cant_curvas,bins])
    ch1 = np.reshape(ch1,[cant_curvas,bins])
    
    ch0 = ch0/(2**14)
    ch1 = ch1*0.2/(2**15)
    
    for j in range(cant_curvas):
        lines0[j][0].set_ydata(ch0[j,:]) 
        
    ch0_mean = np.mean(ch0,axis=0)
    #ch0_mvg = np.convolve(ch0_mean,np.ones(mvg_avg_window)/mvg_avg_window,mode='valid')
    ch0_mvg = pd.rolling_mean(ch0_mean,mvg_avg_window,center=True)
    ch0_std = pd.rolling_std(ch0_mean,mvg_avg_window,center=True)
    ch0_std = ch0_std/ch0_mvg
    print ch0_mvg.shape
    
    lines0[cant_curvas][0].set_ydata(ch0_mvg)     
    lines0[cant_curvas+1][0].set_ydata(ch0_std)
	
    for j in range(cant_curvas):
        lines1[j][0].set_ydata(ch1[j,:]) 
             

    tiempo_actual = datetime.datetime.now()
    time_str = datetime.datetime.strftime(tiempo_actual,'%Y-%m-%d %H:%M:%S')    
    t0.set_text('T:' + str(time_str))
    
#    ax0.plot(np.transpose(ch0),color='b',linewidth=0.5)
#    ax0.set_ylim([0,0.075])
#    
#    ax1.plot(np.transpose(ch1),color='b',linewidth=0.5)
#    ax1.set_ylim([0,0.025])
    
    return lines0, lines1,
    
    
    
    
        
#    ax.plot(xx1[0:yy1.size],yy1,'-')
#    ax.set_ylim([0,80])

#    ax2 = ax.twinx()
#    ax.plot(media_acc,color='b')
#    ax.set_xlim([0,199])
#    ax.set_ylim([0,15000])
    
#    ax2.plot(snr_acc,color='r')
#    ax2.set_ylim([0,300])

#    return line,


# Init only required for blitting to give a clean slate.
def init():
    global x0,x1
    
    for i in range(cant_curvas):
        lines0[i][0].set_ydata(x0) 

    for i in range(cant_curvas):
        lines1[i][0].set_ydata(x1) 
     
    return lines0, lines1,

ani = animation.FuncAnimation(fig, animate, init_func=init,
                              interval=100, blit=False)
plt.show()