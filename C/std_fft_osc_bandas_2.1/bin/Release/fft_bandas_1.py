#!/usr/bin/env python
"""
An animated image
"""
import win32pipe, win32file,time,struct
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import Tkinter as Tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing import Process
from timeit import default_timer as timer
import sys
import datetime 


fileHandle = win32file.CreateFile("\\\\.\\pipe\\PipeFFT_bandas",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)                            
tam=int(sys.argv[1])
qFreq=int(sys.argv[2])
banda_ai = int(sys.argv[3])
banda_af = int(sys.argv[4])
banda_bi = int(sys.argv[5])
banda_bf = int(sys.argv[6])
banda_ci = int(sys.argv[7])
banda_cf = int(sys.argv[8])

c = 300000000;
n = 1.46;
c_f = c/n;
delta_t = 5e-9;
delta_x = qFreq*c_f*delta_t/2;


vertical=200
data_a=np.zeros((vertical,tam))
data_b=np.zeros((vertical,tam))
data_c=np.zeros((vertical,tam))


t = 0
def updatefig2(*args):
    global data_a,data_b,data_c, fileHandle
    
    global mi_var, ma_var, ch_caxis
    global ch_caxis_banda1, ch_caxis_banda2, ch_caxis_banda3
    global data
#    global mi_var_b, ma_var_b, ch_caxis_b
#    global mi_var_c, ma_var_c, ch_caxis_c
    global t
    

    mi_var = float(min_var.get())
    ma_var = float(max_var.get())
    ch_caxis = check_caxis.get()      
    
    ch_caxis_banda1 = check_caxis_banda1.get()  
    ch_caxis_banda2 = check_caxis_banda2.get()  
    ch_caxis_banda3 = check_caxis_banda3.get()  

#    mi_var_b = float(min_var_b.get())
#    ma_var_b = float(max_var_b.get())
#    ch_caxis_b = check_caxis_b.get()   
#    
#    mi_var_c = float(min_var_c.get())
#    ma_var_c = float(max_var_c.get())
#    ch_caxis_c = check_caxis_c.get()       
    
    
    f=(args[0])       
    rr,rd = win32file.ReadFile(fileHandle, tam*4*3) #2 es tamanio de datos   
    actual = np.frombuffer(rd,dtype=np.float32) 
    
    act_banda_a = actual[0:tam:]
    act_banda_b = actual[tam:2*tam:]
    act_banda_c = actual[2*tam:3*tam:]
    
    
    if (f>0 and (f)%vertical==0 ):
        data_a=np.zeros((vertical,tam))
        data_b=np.zeros((vertical,tam))
        data_c=np.zeros((vertical,tam))
        
        
    data_a[f%vertical]=act_banda_a
    data_b[f%vertical]=act_banda_b
    data_c[f%vertical]=act_banda_c    
                   
    #data=np.random.rand(60,tam)*f/100 
    # Imagen  
    
    data = np.zeros((vertical,tam))
    if (ch_caxis_banda1==1): 
        data = data + data_a

    if (ch_caxis_banda2==1): 
        data = data + data_b
        
    if (ch_caxis_banda3==1): 
        data = data + data_c        
    
    im.set_array(data)
#    im_b.set_array(data_b)
#    im_c.set_array(data_c)
    
    if (ch_caxis==1):
        im.set_clim([data.min(),data.max()])
    else:
        im.set_clim([mi_var,ma_var])   
        
#    if (ch_caxis_b==1):
#        im_b.set_clim([data_b.min(),data_b.max()])
#    else:
#        im_b.set_clim([mi_var_b,ma_var_b])   
#        
#    if (ch_caxis_c==1):
#        im_c.set_clim([data_c.min(),data_c.max()])
#    else:
#        im_c.set_clim([mi_var_c,ma_var_c])           


    t = t + 1;    
    
    
    return im,#im_b,im_c,




root = Tk.Tk()



# Imagen
min_var = Tk.StringVar()
entrada_min = Tk.Entry(root, width=5, textvariable=min_var)
entrada_min.grid(column=1,row=3)
entrada_minL=Tk.Label(root,text="Caxis min: ")
entrada_minL.grid(column=0,row=3)
text = min_var.get()
min_var.set(0)

max_var = Tk.StringVar()
entrada_max = Tk.Entry(root, width=5, textvariable=max_var)
entrada_max.grid(column=1,row=4)
entrada_maxL=Tk.Label(root,text="Caxis max: ")
entrada_maxL.grid(column=0,row=4)
text = max_var.get()
max_var.set(0.35)

check_caxis = Tk.IntVar()
caxis_box=Tk.Checkbutton(root,text="Caxis Min-Max",variable=check_caxis)
caxis_box.grid(column=2,row=3)

check_caxis_banda1 = Tk.IntVar()
caxis_box_banda1=Tk.Checkbutton(root,text="Banda A (" + str(banda_ai) + " - " + str(banda_af) + " Hz)" ,variable=check_caxis_banda1)
caxis_box_banda1.grid(column=0,row=2)

check_caxis_banda2 = Tk.IntVar()
caxis_box_banda2=Tk.Checkbutton(root,text="Banda B (" + str(banda_bi) + " - " + str(banda_bf) + " Hz)" ,variable=check_caxis_banda2)
caxis_box_banda2.grid(column=1,row=2)

check_caxis_banda3 = Tk.IntVar()
caxis_box_banda3=Tk.Checkbutton(root,text="Banda C (" + str(banda_ci) + " - " + str(banda_cf) + " Hz)" ,variable=check_caxis_banda3)
caxis_box_banda3.grid(column=2,row=2)

####
#min_var_b = Tk.StringVar()
#entrada_min_b = Tk.Entry(root, width=5, textvariable=min_var_b)
#entrada_min_b.grid(column=1,row=4)
#entrada_minL_b=Tk.Label(root,text="Caxis min banda B: ")
#entrada_minL_b.grid(column=0,row=4)
#text_b = min_var_b.get()
#min_var_b.set(0)
#
#max_var_b = Tk.StringVar()
#entrada_max_b = Tk.Entry(root, width=5, textvariable=max_var_b)
#entrada_max_b.grid(column=1,row=5)
#entrada_maxL_b=Tk.Label(root,text="Caxis max banda B: ")
#entrada_maxL_b.grid(column=0,row=5)
#text_b = max_var_b.get()
#max_var_b.set(0.35)
#
#check_caxis_b = Tk.IntVar()
#caxis_box_b=Tk.Checkbutton(root,text="Caxis Min-Max B",variable=check_caxis_b)
#caxis_box_b.grid(column=2,row=4)
#
################
#min_var_c = Tk.StringVar()
#entrada_min_c = Tk.Entry(root, width=5, textvariable=min_var_c)
#entrada_min_c.grid(column=1,row=6)
#entrada_minL_c=Tk.Label(root,text="Caxis min banda C: ")
#entrada_minL_c.grid(column=0,row=6)
#text_c = min_var_c.get()
#min_var_c.set(0)
#
#max_var_c = Tk.StringVar()
#entrada_max_c = Tk.Entry(root, width=5, textvariable=max_var_c)
#entrada_max_c.grid(column=1,row=7)
#entrada_maxL_c=Tk.Label(root,text="Caxis max banda C: ")
#entrada_maxL_c.grid(column=0,row=7)
#text_c = max_var_c.get()
#max_var_c.set(0.35)
#
#check_caxis_c = Tk.IntVar()
#caxis_box_c=Tk.Checkbutton(root,text="Caxis Min-Max C",variable=check_caxis_c)
#caxis_box_c.grid(column=2,row=6)
#
######################################

label = Tk.Label(root,text="ADQUISICION DAS").grid(column=0, row=0,columnspan=10)
fig=Figure(figsize=(15, 6), dpi=125)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1,columnspan=10)

# Ax1
ax = fig.add_axes([.03,.1,.87,.72]) 
im = ax.imshow(data_a, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
fig.colorbar(im)
#ax_a.set_title('Banda A: ' + str(banda_ai) + ' - ' + str(banda_af) + ' Hz')

#ax_b = fig.add_axes([.36,.1,.27,.72]) 
#im_b = ax_b.imshow(data_b, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
#fig.colorbar(im_b)
#ax_b.set_title('Banda B: ' + str(banda_bi) + ' - ' + str(banda_bf) + ' Hz')
#
#ax_c = fig.add_axes([.7,.1,.27,.72]) 
#im_c = ax_c.imshow(data_c, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
#fig.colorbar(im_c)
#ax_c.set_title('Banda C: ' + str(banda_ci) + ' - ' + str(banda_cf) + ' Hz')


   
ani = animation.FuncAnimation(fig, updatefig2, interval=100, blit=False)
plt.show()
Tk.mainloop()
