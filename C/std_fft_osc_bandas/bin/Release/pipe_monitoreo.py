# -*- coding: utf-8 -*-
"""
Created on Thu Oct 06 13:58:22 2016

@author: hh_s
"""

"""
A simple example of an animated plot
"""
import numpy as np
import win32pipe, win32file,time,struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import seaborn
import sys
import numpy.fft as fft

fileHandle = win32file.CreateFile("\\\\.\\pipe\\Pipe2",
                              win32file.GENERIC_READ,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)

#tam=10000
bin1=int(sys.argv[1])
energia_size_laser=int(sys.argv[2])
energia_size_edfa=int(sys.argv[3])
bin_mon_laser_i = int(sys.argv[4])
bin_mon_laser_f = int(sys.argv[5])
bin_mon_edfa_i = int(sys.argv[6])
bin_mon_edfa_f = int(sys.argv[7])
cLASER = float(sys.argv[8])
cEDFA = float(sys.argv[9])
tam = bin1 + energia_size_laser + energia_size_edfa


print "pipe adentro", tam


fig,([ax1,ax2],[ax3,ax4]) = plt.subplots(2,2)

x1=np.random.uniform(0.05,0.1,size=(500,1))
ax1 = plt.subplot2grid((2, 8), (0, 0), colspan=4)
ax11 = ax1.twinx()
line1, = ax1.plot(x1)
line11, = ax11.plot(x1)

x2=np.random.uniform(0.05,0.1,size=(500,1))
ax2 = plt.subplot2grid((2, 8), (1, 0), colspan=4)
ax22 = ax2.twinx()
line2, = ax2.plot(x2)
line22, = ax22.plot(x2)

x3=np.random.uniform(0.05,0.1,size=(500,1))
ax3 = plt.subplot2grid((2, 8), (0, 5), colspan=3)
ax33 = ax3.twinx()
line3, = ax3.plot(x3)
line33, = ax33.plot(x3)

x4=np.random.uniform(0.05,0.1,size=(500,1))
ax4 = plt.subplot2grid((2, 8), (1, 5), colspan=3)
ax44 = ax4.twiny()
line4, = ax4.plot(x4)
line44, = ax44.plot(x4)

media_acc_edfa = np.zeros(200)
snr_acc_edfa = np.zeros(200)

media_acc_laser = np.zeros(200)
snr_acc_laser = np.zeros(200)

perfil_laser = np.zeros(400)
perfil_edfa = np.zeros(400)

rango1 = []
rango2 = []
j = 0

def animate(i):
    #line.set_ydata(x+i/100.0)  # update the data
    #return line,
   # if(i%15==0 and i>0):
       
    global rango1, rango2   
    global j 
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()
    ax11.cla()
    ax22.cla()
    ax33.cla()
    ax44.cla()    
    
#    ax.plot(x+i/10.0,'.')
    rr,rd = win32file.ReadFile(fileHandle,tam*4)
    super_vector = np.frombuffer(rd,dtype=np.float32)
    perfil = super_vector[0:(bin1-1)]  
    
    energia_laser = super_vector[bin1:(bin1+energia_size_laser-1)]    
    energia_edfa = super_vector[bin1+energia_size_laser:(bin1+energia_size_laser+energia_size_edfa-1)]  
    
    energia_laser = energia_laser*cLASER*2/pow(2,15)*5;
    energia_edfa = energia_edfa*cEDFA*2/pow(2,15)*5;
    
    perfil_laser[bin_mon_laser_i-2:bin_mon_laser_f+2] = cLASER*perfil[bin_mon_laser_i-2:bin_mon_laser_f+2]*2/pow(2,15)
    perfil_edfa[bin_mon_edfa_i-2:bin_mon_edfa_f+2] = cEDFA*perfil[bin_mon_edfa_i-2:bin_mon_edfa_f+2]*2/pow(2,15)
    
    
    media_laser = np.mean(energia_laser)
    std_laser = np.std(energia_laser)
    
    media_edfa = np.mean(energia_edfa)
    std_edfa = np.std(energia_edfa)    
    
#    if (i%200==0): 
#        
#        media_acc = np.zeros(200)
#        snr_acc = np.zeros(200)
    
    media_acc_laser[i%200] = media_laser
    snr_acc_laser[i%200] = media_laser/std_laser
    
    media_acc_edfa[i%200] = media_edfa
    snr_acc_edfa[i%200] = media_edfa/std_edfa    
    
    if (j == 0):
        rango1 = np.array([media_laser-20*std_laser, media_laser+10*std_laser])
    yy1_laser,xx1_laser = np.histogram(energia_laser,200,rango1)
    
    if (j == 0):
        rango2 = np.array([media_edfa-10*std_edfa, media_edfa+20*std_edfa])
    yy1_edfa,xx1_edfa = np.histogram(energia_edfa,200,rango2)
    
    fft_laser = fft.fft(energia_laser)
    fft_laser = fft_laser[0:len(energia_laser)/2+1:]
    fft_laser = abs(fft_laser)
    fft_edfa = fft.fft(energia_edfa)
    fft_edfa = fft_edfa[0:len(energia_edfa)/2+1:]
    fft_edfa = abs(fft_edfa)    
    
    ax1.plot(media_acc_laser,color='b')
    ax1.set_title('Energia media')
    ax1.set_ylim([0,10])
    ax11.plot(media_acc_edfa,color='r')
    ax11.set_ylim([0,100])
    ax1.set_ylabel('Energia Laser [nJ]',color='b')
    ax11.set_ylabel('Energia EDFA [nJ]',color='r')
    ax1.legend('Laser')    
    ax11.legend('EDFA')   

    ax2.plot(snr_acc_laser,color='b')
    ax2.set_title('Energia SNR')
    ax2.set_ylim([0,400])
    ax22.plot(snr_acc_edfa,color='r')
    ax22.set_ylim([0,400])    
    ax2.set_ylabel('SNR Energia Laser',color='b')
    ax22.set_ylabel('SNR Energia EDFA',color='r')        
    
    ax3.plot(perfil_laser,color='b')
    ax33.plot(perfil_edfa,color='r')
    ax3.set_title('Perfil')
    ax3.set_xlim([0,200])
    ax33.set_xlim([0,200])
    ax3.set_ylabel('Potencia Laser [W]',color='b')
    ax33.set_ylabel('Potencia EDFA [W]',color='r')        

#    ax4.plot(xx1_laser[1::],yy1_laser,color='b')  
#    ax44.plot(xx1_edfa[1::],yy1_edfa,color='r')  

    ax4.plot(fft_laser/fft_laser[0],color='b')  
    ax44.plot(fft_edfa/fft_edfa[0],color='r')  
    ax4.set_xlim([0,101])
    ax44.set_xlim([0,101])
    ax4.set_ylim([0,0.002])
    ax44.set_ylim([0,0.002])      
    #ax4.set_xlim([8500,11000])
    #ax4.set_ylim([0,300]) 
    ax4.set_ylabel('Cuentas')
    ax4.set_xlabel('Energia Laser [nJ]',color='b')
    ax44.set_xlabel('Energia EDFA [nJ]',color='r')        
    
    j = j+1
    return line1, line2, line3, line4, line11, line22, line33, line44,
    
    
    
        
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
    line1.set_ydata(x1)
    line2.set_ydata(x2)
    line3.set_ydata(x3)
    line4.set_ydata(x4)   
    line11.set_ydata(x1)
    line22.set_ydata(x2)
    line33.set_ydata(x3)
    line44.set_ydata(x4)       
    return line1, line2, line3, line4, line11, line22, line33, line44,

ani = animation.FuncAnimation(fig, animate, init_func=init,
                              interval=100, blit=False)
plt.show()