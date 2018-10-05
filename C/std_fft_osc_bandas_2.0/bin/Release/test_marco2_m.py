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

fileHandle = win32file.CreateFile("\\\\.\\pipe\\Pipe",
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)                            
tam=int(sys.argv[1])
ventana=int(sys.argv[2])

c = 300000000;
n = 1.46;
c_f = c/n;
delta_t = 5e-9;
delta_x = c_f*delta_t/2;


tam=800
ventana = 5;

vertical=200
tam = tam - ventana + 1;

data=np.zeros((vertical,tam))
promedio = np.zeros(tam)

flag_promedio = 0
ind = 0
flag_ch = 0

coord_1 = 0
coord_2 = 0
coord_3 = 0
coord_4 = 0
coord_5 = 0

tra_1 = []
tra_2 = []
tra_3 = []
tra_4 = []
tra_5 = []

tt_1 = []
tt_2 = []
tt_3 = []
tt_4 = []
tt_5 = []

t = 0
def updatefig2(*args):
    global data, fileHandle
    
    global mi_var
    global ma_var
    global ch_caxis, ch1_r, ch2_r, ch3_r, ch4_r, ch5_r
    global tra_1, tra_2, tra_3, tra_4, tra_5
    global tt_1, tt_2, tt_3, tt_4, tt_5
    global t
    global ax2,ax

    global mi_var_p
    global ma_var_p
    global ch_caxis_p  
    global promedio
    global ind
    global flag_promedio
    global coord_1, coord_2, coord_3, coord_4, coord_5

    mi_var = float(min_var.get())
    ma_var = float(max_var.get())
    off_var = float(offset_var.get())
    ch_caxis = check_caxis.get()      
    x_mi_var = float(x_min_var.get())
    x_ma_var = float(x_max_var.get())   
    x_mi_var = np.round((x_mi_var + off_var)/delta_x)
    x_ma_var = np.round((x_ma_var + off_var)/delta_x)
    
    f=(args[0])       
    rr,rd = win32file.ReadFile(fileHandle, tam*4) #2 es tamanio de datos   
    actual = np.frombuffer(rd,dtype=np.float32) 
    
    
    actual = np.random.rand(1,tam);
    
    
    if (f>0 and (f)%vertical==0 ):
        data=np.zeros((vertical,tam))
        data[f%vertical]=actual
    else:       
        data[f%vertical]=actual
                   
    #data=np.random.rand(60,tam)*f/100 
    # Imagen  
    im.set_array(data)
    
    if (ch_caxis==1):
        im.set_clim([data.min(),data.max()])
    else:
        im.set_clim([mi_var,ma_var])   
        
    ax.set_xlim([x_mi_var,x_ma_var])
    ticks = ax.get_xticks()
    ax.set_xticklabels(np.round(ticks*delta_x-float(off_var)))    


    
    # Plot
    mi_var_p = float(min_var_p.get())
    ma_var_p = float(max_var_p.get())
    ch_caxis_p = check_caxis_p.get()        
    ch_actual_p = check_actual.get()   
    #ch_actual_p=1
    #actual = np.frombuffer(rd,dtype=np.float32)   
    
    # Filtro de media en el vector
    #actual = moving_average(actual,5);  
    #print len(actual)    
    
    if (flag_promedio == 0):
        flag_promedio = 1
        ind = 1
        promedio = np.zeros(tam)

    start = timer()     
    ind = ind + 1   
    promedio = (promedio*(ind-1) + actual)/ind
    end = timer()
    print(end - start) 
 
    #promedio = moving_average(promedio,5); 

 
#  PERFIL
    ax1.cla()    
    if (ch_actual_p==1):
        pl1 = ax1.plot(actual,'r')
        
    pl1 = ax1.plot(promedio)
    ax1.axes.xaxis.set_ticklabels([])
    ax1.set_xlim([0,tam])
    if (ch_caxis_p!=1):
        ax1.set_ylim([mi_var_p,ma_var_p])   
    else:
        ax1.set_ylim([actual.min(),actual.max()])   
    ax1.set_xlim([x_mi_var,x_ma_var])
    
    ch1_r_v = ch1_r.get()    
    ch2_r_v = ch2_r.get()  
    ch3_r_v = ch3_r.get()  
    ch4_r_v = ch4_r.get()  
    ch5_r_v = ch5_r.get()  
    
    if (ch1_r_v == 1):
        xx1 = [coord_1, coord_1]
        yy1 = [0, ma_var_p]
        pl1 = ax1.plot(xx1,yy1,'-r')
 
    if (ch2_r_v == 1):
        xx1 = [coord_2, coord_2]
        yy1 = [0, ma_var_p]
        pl1 = ax1.plot(xx1,yy1,'-g')

    if (ch3_r_v == 1):
        xx1 = [coord_3, coord_3]
        yy1 = [0, ma_var_p]
        pl1 = ax1.plot(xx1,yy1,'-y')

    if (ch4_r_v == 1):
        xx1 = [coord_4, coord_4]
        yy1 = [0, ma_var_p]
        pl1 = ax1.plot(xx1,yy1,'-k')

    if (ch5_r_v == 1):
        xx1 = [coord_5, coord_5]
        yy1 = [0, ma_var_p]
        pl1 = ax1.plot(xx1,yy1,'-b')      
        
# TRAYECTORIA  

#    if (ch1_r_v == 1): 
#        tt_1.append(t)
#        tra_1.append(actual[coord_1])
#        pl2 = ax2.plot(tt_1,tra_1,'-r') 

#    if (ch2_r_v == 1): 
#        tt_2.append(t)
#        tra_2.append(actual[coord_2])
#        pl2 = ax2.plot(tt_2,tra_2,'g')
#
#    if (ch3_r_v == 1): 
#        tt_3.append(t)
#        tra_3.append(actual[coord_3])
#        pl2 = ax2.plot(tt_3,tra_3,'y')
#
#    if (ch4_r_v == 1): 
#        tt_4.append(t)
#        tra_4.append(actual[coord_1])
#        pl2 = ax2.plot(tt_4,tra_4,'k')
#
#    if (ch5_r_v == 1): 
#        tt_5.append(t)
#        tra_5.append(actual[coord_5])
#        pl2 = ax2.plot(tt_5,tra_5,'b')        

    t = t + 1;    
    
    
    print data.min(),data.max()
    return im, pl1, 

def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def callback_reset_promedio():
    global flag_promedio
    flag_promedio = 0    
    return flag_promedio,
    
#def callback_reset_perfil():
#    global tra_1, tra_2, tra_3, tra_4, tra_5
#    global tt_1, tt_2, tt_3, tt_4, tt_5
#    global t
#    
#    tra_1 = []
#    tra_2 = []
#    tra_3 = []
#    tra_4 = []
#    tra_5 = []
#    
#    tt_1 = []
#    tt_2 = []
#    tt_3 = []
#    tt_4 = []
#    tt_5 = []
#    
#    t = 0   
#    ax2.cla() 
    
    
def sel():
    global cid
    global var_radio, var_radio_b
    global fig
    global flag_ch

    var_radio_b = var_radio.get()   
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
 
def onclick(event):
    global ix, iy, cid
    global var_radio_b
    global coord_1, coord_2, coord_3, coord_4, coord_5 
    global var1, var2, var3, var4, var5 
    global fig
    global flag_ch
    ix, iy = event.xdata, event.ydata
    print 'x = %d, y = %d'%(ix, iy)
    
    off_var = float(offset_var.get())
    
    if (var_radio_b == 1):
        coord_1 = ix
        var1.set(round((coord_1*delta_x-float(off_var))*10)/10)
    elif (var_radio_b == 2):
        coord_2 = ix
        var2.set(round((coord_2*delta_x-float(off_var))*10)/10)
    elif (var_radio_b == 3):
        coord_3 = ix
        var3.set(round((coord_3*delta_x-float(off_var))*10)/10)
    elif (var_radio_b == 4):
        coord_4 = ix
        var4.set(round((coord_4*delta_x-float(off_var))*10)/10)
    elif (var_radio_b == 5):
        coord_5 = ix    
        var5.set(round((coord_5*delta_x-float(off_var))*10)/10)
        
        
        


root = Tk.Tk()

# Boton reset
boton_reset = Tk.Button(root, text="Reset Promedio", command=callback_reset_promedio)
boton_reset.grid(column=7,row=2)

# Boton reset
#boton_reset_perfil = Tk.Button(root, text="Reset Perfil", command=callback_reset_perfil)
#boton_reset_perfil.grid(column=7,row=3)

# Imagen
min_var = Tk.StringVar()
entrada_min = Tk.Entry(root, width=5, textvariable=min_var)
entrada_min.grid(column=1,row=2)
entrada_minL=Tk.Label(root,text="Caxis min: ")
entrada_minL.grid(column=0,row=2)
text = min_var.get()
min_var.set(0)

max_var = Tk.StringVar()
entrada_max = Tk.Entry(root, width=5, textvariable=max_var)
entrada_max.grid(column=1,row=3)
entrada_maxL=Tk.Label(root,text="Caxis max: ")
entrada_maxL.grid(column=0,row=3)
text = max_var.get()
max_var.set(0.35)

offset_var = Tk.StringVar()
offset = Tk.Entry(root, width=5, textvariable=offset_var)
offset.grid(column=1,row=4)
offset_L=Tk.Label(root,text="Offset: ")
offset_L.grid(column=0,row=4)
text = offset_var.get()
offset_var.set(0)


x_L=Tk.Label(root,text="Zoom x: ")
x_L.grid(column=0,row=6)
x_min_var = Tk.StringVar()
x_min = Tk.Entry(root, width=5, textvariable=x_min_var)
x_min.grid(column=1,row=6)
text = min_var.get()
x_min_var.set(0)

x_max_var = Tk.StringVar()
x_max = Tk.Entry(root, width=5, textvariable=x_max_var)
x_max.grid(column=1,row=7)
text = max_var.get()
x_max_var.set(np.round(tam*delta_x))


check_caxis = Tk.IntVar()
caxis_box=Tk.Checkbutton(root,text="Caxis Min-Max",variable=check_caxis)
caxis_box.grid(column=2,row=2)

# PLot
min_var_p = Tk.StringVar()
entrada_min_p = Tk.Entry(root, width=5, textvariable=min_var_p)
entrada_min_p.grid(column=4,row=2)
entrada_minL_p=Tk.Label(root,text="Plot min: ")
entrada_minL_p.grid(column=3,row=2)
text = min_var_p.get()
min_var_p.set(0)

max_var_p = Tk.StringVar()
entrada_max_p = Tk.Entry(root, width=5, textvariable=max_var_p)
entrada_max_p.grid(column=4,row=3)
entrada_maxL_p=Tk.Label(root,text="Plot max: ")
entrada_maxL_p.grid(column=3,row=3)
text = max_var_p.get()
max_var_p.set(0.4)

check_caxis_p = Tk.IntVar()
caxis_box_p=Tk.Checkbutton(root,text="Plot Min-Max",variable=check_caxis_p)
caxis_box_p.grid(column=5,row=2)

check_actual = Tk.IntVar()
check_actual.set(1)
ch_actual=Tk.Checkbutton(root,text="Perfil actual",variable=check_actual)
ch_actual.grid(column=5,row=3)

# Radio button para dibujar linea
var_radio = Tk.IntVar()
R1 = Tk.Radiobutton(root, text="Rojo", variable=var_radio, value=1,command=sel)
R1.grid(column=9,row=2)
R2 = Tk.Radiobutton(root, text="Verde", variable=var_radio, value=2,command=sel)
R2.grid(column=9,row=3)
R3 = Tk.Radiobutton(root, text="Amarillo", variable=var_radio, value=3,command=sel)
R3.grid(column=9,row=4)
R4 = Tk.Radiobutton(root, text="Negro", variable=var_radio, value=4,command=sel)
R4.grid(column=9,row=5)
R5 = Tk.Radiobutton(root, text="Azul", variable=var_radio, value=5,command=sel)
R5.grid(column=9,row=6)
label_radio = Tk.Label(root)

# Check boxes colores
ch1_r = Tk.IntVar()
box_ch1_r=Tk.Checkbutton(root,text="",variable=ch1_r)
box_ch1_r.grid(column=8,row=2)
ch2_r = Tk.IntVar()
box_ch2_r=Tk.Checkbutton(root,text="",variable=ch2_r)
box_ch2_r.grid(column=8,row=3)
ch3_r = Tk.IntVar()
box_ch3_r=Tk.Checkbutton(root,text="",variable=ch3_r)
box_ch3_r.grid(column=8,row=4)
ch4_r = Tk.IntVar()
box_ch4_r=Tk.Checkbutton(root,text="",variable=ch4_r)
box_ch4_r.grid(column=8,row=5)
ch5_r = Tk.IntVar()
box_ch5_r=Tk.Checkbutton(root,text="",variable=ch5_r)
box_ch5_r.grid(column=8,row=6)


root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_columnconfigure(6, weight=1)
root.grid_columnconfigure(7, weight=1)
root.grid_columnconfigure(8, weight=1)
root.grid_columnconfigure(9, weight=1)


var1 = Tk.StringVar()
var2 = Tk.StringVar()
var3 = Tk.StringVar()
var4 = Tk.StringVar()
var5 = Tk.StringVar()
var1.set('0')
var2.set('0')
var3.set('0')
var4.set('0')
var5.set('0')
l1 = Tk.Label(root, textvariable = var1)
l2 = Tk.Label(root, textvariable = var2)
l3 = Tk.Label(root, textvariable = var3)
l4 = Tk.Label(root, textvariable = var4)
l5 = Tk.Label(root, textvariable = var5)
l1.grid(column=10,row=2)
l2.grid(column=10,row=3)
l3.grid(column=10,row=4)
l4.grid(column=10,row=5)
l5.grid(column=10,row=6)


label = Tk.Label(root,text="ADQUISICION DAS").grid(column=0, row=0,columnspan=10)
fig=Figure(figsize=(6, 4), dpi=125)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1,columnspan=10)

# Ax1
ax = fig.add_axes([.1,.1,.8,.72]) 
im = ax.imshow(data, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
fig.colorbar(im)

ax1 = fig.add_axes([.1,.86,.64,.11]) 
pl1 = ax1.plot(promedio)
ax1.axes.xaxis.set_ticklabels([])
ax1.set_xlim([0,tam])
ax1.set_ylim([-0.001,0.001])


#ax2 = fig.add_axes([.1,.78,.64,.20]) 
#line_1, = ax2.plot([], [], lw=2)
#ax2.axes.xaxis.set_ticklabels([])


cid = fig.canvas.mpl_connect('button_press_event', onclick)
   
ani = animation.FuncAnimation(fig, updatefig2, interval=100, blit=False)
plt.show()
Tk.mainloop()
