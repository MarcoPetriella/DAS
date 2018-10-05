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


pipeRead=win32file.CreateFile("\\\\.\\pipe\\pipeParametrosCWrite",
                                win32file.GENERIC_READ ,#verificar el nombre que tiene este pipe en C
                                0,None,
                                win32file.OPEN_EXISTING,
                                0,None)
pipeWrite=win32file.CreateFile("\\\\.\\pipe\\pipeParametrosCRead",
                                win32file.GENERIC_WRITE ,#verificar el nombre que tiene este pipe en C
                                0,None,
                                win32file.OPEN_EXISTING,
                                0,None)



tam=int(sys.argv[1])
qFreq=int(sys.argv[2])
filas=int(sys.argv[3])

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
    
    global mi_var_a, ma_var_a, ch_caxis_a
    global mi_var_b, ma_var_b, ch_caxis_b
    global mi_var_c, ma_var_c, ch_caxis_c
    global t
    

    mi_var_a = float(min_var_a.get())
    ma_var_a = float(max_var_a.get())
    ch_caxis_a = check_caxis_a.get()      

    mi_var_b = float(min_var_b.get())
    ma_var_b = float(max_var_b.get())
    ch_caxis_b = check_caxis_b.get()   
    
    mi_var_c = float(min_var_c.get())
    ma_var_c = float(max_var_c.get())
    ch_caxis_c = check_caxis_c.get()       
    
    
    f=(args[0])       
    rr,rd = win32file.ReadFile(fileHandle, tam*4*3) #2 es tamanio de datos   
    actual = np.frombuffer(rd,dtype=np.float32) 
    
    rr,rd = win32file.ReadFile(pipeRead, 6*4) #2 es tamanio de datos   
    parametros = np.frombuffer(rd,dtype=np.int)  
    ax_a.set_title('Banda A: ' + str(parametros[0]) + ' - ' + str(parametros[1]) + ' Hz')
    ax_b.set_title('Banda B: ' + str(parametros[2]) + ' - ' + str(parametros[3]) + ' Hz')
    ax_c.set_title('Banda C: ' + str(parametros[4]) + ' - ' + str(parametros[5]) + ' Hz')
    
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
    im_a.set_array(data_a)
    im_b.set_array(data_b)
    im_c.set_array(data_c)
    
    if (ch_caxis_a==1):
        im_a.set_clim([data_a.min(),data_a.max()])
    else:
        im_a.set_clim([mi_var_a,ma_var_a])   
        
    if (ch_caxis_b==1):
        im_b.set_clim([data_b.min(),data_b.max()])
    else:
        im_b.set_clim([mi_var_b,ma_var_b])   
        
    if (ch_caxis_c==1):
        im_c.set_clim([data_c.min(),data_c.max()])
    else:
        im_c.set_clim([mi_var_c,ma_var_c])           


    t = t + 1;   
    
    banda_ai_s = int(scale_ai.get())
    banda_af_s = int(scale_af.get())
    banda_bi_s = int(scale_bi.get())
    banda_bf_s = int(scale_bf.get())
    banda_ci_s = int(scale_ci.get())
    banda_cf_s = int(scale_cf.get())
    
    stringi = '%06d' % (banda_ai_s) + "," + '%06d' % (banda_af_s) + "," + '%06d' % (banda_bi_s) + "," + '%06d' % (banda_bf_s) + "," + '%06d' % (banda_ci_s) + "," + '%06d' % (banda_cf_s)
    
    win32file.WriteFile(pipeWrite,stringi)
    
    
    
    return im_a,im_b,im_c,




root = Tk.Tk()



# Imagen
min_var_a = Tk.StringVar()
entrada_min_a = Tk.Entry(root, width=5, textvariable=min_var_a)
entrada_min_a.grid(column=1,row=2)
entrada_minL_a=Tk.Label(root,text="Caxis min banda A: ")
entrada_minL_a.grid(column=0,row=2)
text_a = min_var_a.get()
min_var_a.set(0)

max_var_a = Tk.StringVar()
entrada_max_a = Tk.Entry(root, width=5, textvariable=max_var_a)
entrada_max_a.grid(column=1,row=3)
entrada_maxL_a=Tk.Label(root,text="Caxis max banda A: ")
entrada_maxL_a.grid(column=0,row=3)
text_a = max_var_a.get()
max_var_a.set(0.005)

check_caxis_a = Tk.IntVar()
caxis_box_a=Tk.Checkbutton(root,text="Caxis Min-Max A",variable=check_caxis_a)
caxis_box_a.grid(column=2,row=2)

###
min_var_b = Tk.StringVar()
entrada_min_b = Tk.Entry(root, width=5, textvariable=min_var_b)
entrada_min_b.grid(column=1,row=4)
entrada_minL_b=Tk.Label(root,text="Caxis min banda B: ")
entrada_minL_b.grid(column=0,row=4)
text_b = min_var_b.get()
min_var_b.set(0)

max_var_b = Tk.StringVar()
entrada_max_b = Tk.Entry(root, width=5, textvariable=max_var_b)
entrada_max_b.grid(column=1,row=5)
entrada_maxL_b=Tk.Label(root,text="Caxis max banda B: ")
entrada_maxL_b.grid(column=0,row=5)
text_b = max_var_b.get()
max_var_b.set(0.005)

check_caxis_b = Tk.IntVar()
caxis_box_b=Tk.Checkbutton(root,text="Caxis Min-Max B",variable=check_caxis_b)
caxis_box_b.grid(column=2,row=4)

###############
min_var_c = Tk.StringVar()
entrada_min_c = Tk.Entry(root, width=5, textvariable=min_var_c)
entrada_min_c.grid(column=1,row=6)
entrada_minL_c=Tk.Label(root,text="Caxis min banda C: ")
entrada_minL_c.grid(column=0,row=6)
text_c = min_var_c.get()
min_var_c.set(0)

max_var_c = Tk.StringVar()
entrada_max_c = Tk.Entry(root, width=5, textvariable=max_var_c)
entrada_max_c.grid(column=1,row=7)
entrada_maxL_c=Tk.Label(root,text="Caxis max banda C: ")
entrada_maxL_c.grid(column=0,row=7)
text_c = max_var_c.get()
max_var_c.set(0.005)

check_caxis_c = Tk.IntVar()
caxis_box_c=Tk.Checkbutton(root,text="Caxis Min-Max C",variable=check_caxis_c)
caxis_box_c.grid(column=2,row=6)

#####################################

#text_ba=Tk.Label(root,text="Banda A")
#text_ba.grid(column=3,row=2)

var_ai = Tk.IntVar()
scale_ai = Tk.Scale( root, variable = var_ai, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_ai.set(1)
scale_ai.grid(column=3,row=2, rowspan=2)

var_af = Tk.IntVar()
scale_af = Tk.Scale( root, variable = var_af, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_af.set(15)
scale_af.grid(column=4,row=2, rowspan=2)
###

#text_bb=Tk.Label(root,text="Banda B")
#text_bb.grid(column=3,row=4)

var_bi = Tk.IntVar()
scale_bi = Tk.Scale( root, variable = var_bi, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_bi.set(15)
scale_bi.grid(column=3,row=4, rowspan=2)

var_bf = Tk.IntVar()
scale_bf = Tk.Scale( root, variable = var_bf, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_bf.set(40)
scale_bf.grid(column=4,row=4, rowspan=2)
###

#text_bc=Tk.Label(root,text="Banda C")
#text_bc.grid(column=3,row=6)

var_ci = Tk.IntVar()
scale_ci = Tk.Scale( root, variable = var_ci, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_ci.set(40)
scale_ci.grid(column=3,row=6, rowspan=2)

var_cf = Tk.IntVar()
scale_cf = Tk.Scale( root, variable = var_cf, orient='horizontal', from_=0, to=100, width=10, length=200)
scale_cf.set(70)
scale_cf.grid(column=4,row=6, rowspan=2)


banda_ai_s = int(scale_ai.get())
banda_af_s = int(scale_af.get())
banda_bi_s = int(scale_bi.get())
banda_bf_s = int(scale_bf.get())
banda_ci_s = int(scale_ci.get())
banda_cf_s = int(scale_cf.get())

########################

label = Tk.Label(root,text="ADQUISICION DAS").grid(column=0, row=0,columnspan=10)
fig=Figure(figsize=(15, 6), dpi=125)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1,columnspan=10)

# Ax1
ax_a = fig.add_axes([.03,.1,.27,.72]) 
im_a = ax_a.imshow(data_a, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
fig.colorbar(im_a)
ax_a.set_title('Banda A: ' + str(banda_ai_s) + ' - ' + str(banda_af_s) + ' Hz')

ax_b = fig.add_axes([.36,.1,.27,.72]) 
im_b = ax_b.imshow(data_b, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
fig.colorbar(im_b)
ax_b.set_title('Banda B: ' + str(banda_bi_s) + ' - ' + str(banda_bf_s) + ' Hz')

ax_c = fig.add_axes([.7,.1,.27,.72]) 
im_c = ax_c.imshow(data_c, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
fig.colorbar(im_c)
ax_c.set_title('Banda C: ' + str(banda_ci_s) + ' - ' + str(banda_cf_s) + ' Hz')





   
ani = animation.FuncAnimation(fig, updatefig2, interval=100, blit=False)
plt.show()
Tk.mainloop()
