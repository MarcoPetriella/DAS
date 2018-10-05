# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 09:17:11 2018

@author: Marco
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
import serial
import tkFileDialog
import os

laser_onoff = 1
tec_onoff = 1
tec_onoff_bl = 1
seg_onoff_bl = 0
control_int_ext = 0
laser_tension  = 1.15
laser_duracion = 100
laser_frecuencia = 10000
temp_setpoint = 16.55
temp_setpoint_bl = 24
temp_seguidor_bl = -3
flag  = 0
flag1 = 10
offset_corr_laser = 360 + 160
offset_corr_bloque = 360 + 210
mediciones_por_archivo = 2000

arduino = serial.Serial('COM12', 9600, timeout=0.3)

iter_ext = 100
skip_num_ext = 10
temp_amb1_tot1_p = 24
temp_amb2_tot1_p = 24
cont = 0
iter_cont = 5
iter_cont1 = 500
corriente_laser_tot = np.array([])
corriente_bloque_tot = np.array([])
temp_amb1_tot = np.array([])
temp_amb1_tot1 = np.array([])
temp_amb2_tot = np.array([])
temp_amb2_tot1 = np.array([])

start = datetime.datetime.now()
tt = 0
ind_med = 0
ind_arch = 0
guardar_onoff = 0
file_mon = 0
#temp_setpoint = 15

def updatefig2(*args):
    global laser_onoff, tec_onoff, tec_onoff_bl,control_int_ext,control_int_ext1, flag, flag1, offset_corr_laser, offset_corr_bloque, cont, corriente_laser_tot, corriente_bloque_tot, temp_amb1_tot, temp_amb1_tot1, temp_amb2_tot, temp_amb2_tot1,seg_onoff_bl,temp_amb1_tot1_p,temp_amb2_tot1_p
    global mediciones_por_archivo, guardar_onoff, ind_med, filename_path_mon, ind_arch, file_mon
    #global start, tt, temp_setpoint
    
    time.sleep(0.5)
    
    laser_frecuencia = float(frecuencia_var.get())
    laser_duracion = float(ancho_de_pulso_var.get())
    laser_tension = float(tension_laser_var.get())
	
    temp_setpoint = float(temp_set_laser_var.get())
    temp_setpoint_bl = float(temp_set_bloque_var.get())
    temp_seguidor_bl = float(temp_seg_bloque_var.get())
    
#    end = datetime.datetime.now()
#    diff = end-start
#    diff = diff.total_seconds()
    
#    if diff > tt*60:
#        tt = tt+1
#        temp_setpoint = 15.0 + tt*0.1 
#        print temp_setpoint
    
    if seg_onoff_bl == 1:
        temp_setpoint_bl = temp_amb1_tot1_p + temp_seguidor_bl
    
    
#    x = 1./C1*(A1 - 1./temp_set)
#    y = ((B1/3./C1)**3. + (x/2.)**2.)**(1./2.)
#    R = np.exp((y-x/2.)**(1./3.) - (y+x/2.)**(1./3.))
    
    #tension_tec = R*i_bias_laser
    #print tension_tec, frecuencia
    
   # print 'antes out: ',arduino.outWaiting()
    
    #arduino.write(struct.pack('<bffffffffbbb',0,laser_frecuencia,laser_duracion,laser_tension,laser_onoff,tec_onoff,temp_setpoint,tec_onoff_bl,temp_setpoint_bl,control_int_ext,iter_ext,skip_num_ext))
    #arduino.write(struct.pack('<bffffffff',0,laser_frecuencia,laser_duracion,laser_tension,float(laser_onoff),float(tec_onoff),temp_setpoint,float(tec_onoff_bl),temp_setpoint_bl))
    
    if flag == 1:       
        print 'flag1 ini'
        for i in range(10):
            arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))
            arduino.flush()
            time.sleep(0.4)
            flag = 0     
        print 'flag1 fin'
    else:
        arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))    
            
#    print 'control:',control_int_ext
        
    #print 'despues out: ',arduino.outWaiting()
    
#    if control_int_ext == 0:
#        flag1 = flag1 + 1
#        control_int_ext = 1

    #arduino.flushInput()    
    #print 'antes in: ',arduino.inWaiting()
    while arduino.inWaiting():
        a = arduino.read(1)
        b = arduino.read(1)
    #print a,b
    
    #print arduino.readline()
    
    
        if a.isdigit() and b == ',':
            rawString = arduino.readline()
            array_serial = np.fromstring(rawString, dtype=float, count=-1, sep=',')
        
            if len(array_serial) == 13:  
                
                cont = cont + 1
                
                #print array_serial
        
                tension_laser_act = array_serial[10]
                temp_setpoint1 = array_serial[9]
                temp_setpoint_bl1 = array_serial[7]
                temp_laser_actual = array_serial[8]
                temp_bloque_actual = array_serial[6]
                temp_amb1 = array_serial[0]
                temp_amb2 = array_serial[2]
                control_int_ext = int(array_serial[12])
                corriente_laser = array_serial[1]*1000 - offset_corr_laser
                corriente_bloque = array_serial[3]*1000 - offset_corr_bloque                                                    
                corriente_laser_tot = np.append(corriente_laser_tot,corriente_laser)
                corriente_bloque_tot = np.append(corriente_bloque_tot,corriente_bloque)
                temp_amb1_tot = np.append(temp_amb1_tot,temp_amb1)
                temp_amb1_tot1 = np.append(temp_amb1_tot1,temp_amb1)
                
                temp_amb2_tot = np.append(temp_amb2_tot,temp_amb2)
                temp_amb2_tot1 = np.append(temp_amb2_tot1,temp_amb2)                
                                                                 
                if cont > iter_cont:
                    corriente_laser_tot = np.delete(corriente_laser_tot,0)
                    corriente_bloque_tot = np.delete(corriente_bloque_tot,0)
                    temp_amb1_tot = np.delete(temp_amb1_tot,0)
                    temp_amb2_tot = np.delete(temp_amb2_tot,0)
                    
                if cont > iter_cont1:    
                    temp_amb1_tot1 = np.delete(temp_amb1_tot1,0)
                    temp_amb1_tot2 = np.delete(temp_amb2_tot1,0)

                corriente_laser_tot_p = np.mean(corriente_laser_tot)
                corriente_bloque_tot_p = np.mean(corriente_bloque_tot)
                temp_amb1_tot_p = np.mean(temp_amb1_tot)
                temp_amb1_tot1_p = np.mean(temp_amb1_tot1)

                temp_amb2_tot_p = np.mean(temp_amb2_tot)
                temp_amb2_tot1_p = np.mean(temp_amb2_tot1)
                
#                print corriente_laser_tot
#                print corriente_bloque_tot
#                
#                print 'control1:',control_int_ext
#                print ' '
                
                temp_act_laser_var.set('% 6.3f' % temp_laser_actual)
                temp_set1_laser_var.set('% 6.3f' % temp_setpoint1)
                temp_act_bloque_var.set('% 6.3f' % temp_bloque_actual)
                temp_set1_bloque_var.set('% 6.3f' % temp_setpoint_bl1)
                tension_act_laser_var.set('% 6.2f' % tension_laser_act)
                temp_amb1_var.set('% 6.2f' % temp_amb1_tot_p)
                temp_amb2_var.set('% 6.2f' % temp_amb2_tot_p)
                corr_laser_var.set('% 6.2f' % corriente_laser_tot_p)
                corr_bloque_var.set('% 6.2f' % corriente_bloque_tot_p)     
                
                if guardar_onoff == 1:
                    ind_med = ind_med + 1                    
                    ind_med = ind_med%mediciones_por_archivo + 1
                    
                    if ind_med == mediciones_por_archivo:
                        file_mon.close()
                    
                        ind_arch = ind_arch + 1
                        inttostr = '%06d' % (ind_arch)                        
                        file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w') 
                        file_mon.write('hora, control_ext, frecuencia_laser[Hz], ancho_de_pulso[ns], tec_laser_onoff, temp_act_laser[C], temp_set_laser[C], temp_set_laser1[C], tec_bloque_onoff, temp_act_bloque[C], temp_set_bloque[C], temp_set_bloque1[C], temp_seguidor_bloque[C],  modo_seguidor_bloque, tension_laser_act[mV], tension_laser_set[mV], temp_amb1[C], temp_amb2[C], corriente_tec_laser[mA], corriente_tec_bloque[mA] \n')

                    if tec_onoff == 0:
                        tec_onoff_s = 1
                    else:
                        tec_onoff_s = 0
                        
                    if tec_onoff_bl == 0:
                        tec_onoff_bl_s = 1
                    else:
                        tec_onoff_bl_s = 0                        
                        
                    tiempo_actual = datetime.datetime.now()
                    data_string2 = str(tiempo_actual)+ ', ' + str(control_int_ext) + ', ' + str(laser_frecuencia) + ', ' + str(laser_duracion) + ', ' + str(tec_onoff_s) + ', ' + str(temp_laser_actual) + ', ' + str(temp_setpoint)  + ', ' + str(temp_setpoint1) + ', ' + str(tec_onoff_bl_s)  + ', ' + str(temp_bloque_actual) + ', ' + str(temp_setpoint_bl) + ', ' + str(temp_setpoint_bl1) + ', ' + str(temp_seguidor_bl) + ', ' + str(seg_onoff_bl)  + ', ' + str(tension_laser_act)  + ', ' + str(laser_tension*1000)  + ', ' + str(temp_amb1_tot_p) + ', ' + str(temp_amb2_tot_p)  + ', ' + str(corriente_laser_tot_p) + ', ' + str(corriente_laser_tot_p) + '\n'   
                    
                    #print data_string2   
                    
                    if hasattr(file_mon, 'closed'):
                        if not file_mon.closed:                              
                            file_mon.write(data_string2)
                
                
                
            
    #print ' '
    
    while arduino.inWaiting() > 500:
        arduino.readline()
              
    if control_int_ext == 1:
        control_intext_boton['text'] = 'EXT'
    else:
        control_intext_boton['text'] = 'INT'
        
                            
        
    
#    arduino.flushInput()
#    #print 'despues in: ',arduino.inWaiting()


def callback_laser_onoff(*args):
    global laser_onoff
    if laser_onoff == 0:
        laser_onoff = 1
        laser_onoff_boton.config(fg='red')
        laser_onoff_boton['text'] = 'OFF '
    else:
        laser_onoff = 0
        laser_onoff_boton.config(fg='green')
        laser_onoff_boton['text'] = 'ON'


def callback_tec_onoff(*args):
    global tec_onoff
    if tec_onoff == 0:
        tec_onoff = 1
        tec_onoff_boton.config(fg='red')
        tec_onoff_boton['text'] = 'OFF'
    else:
        tec_onoff = 0
        tec_onoff_boton.config(fg='green')  
        tec_onoff_boton['text'] = 'ON '

def callback_tec_onoff_bl(*args):
    global tec_onoff_bl
    if tec_onoff_bl == 0:
        tec_onoff_bl = 1
        tec_onoff_boton_bl.config(fg='red')
        tec_onoff_boton_bl['text'] = 'OFF'
    else:
        tec_onoff_bl = 0
        tec_onoff_boton_bl.config(fg='green')  
        tec_onoff_boton_bl['text'] = 'ON '		

def callback_seg_onoff_bl(*args):
    global seg_onoff_bl
    if seg_onoff_bl == 1:
        seg_onoff_bl = 0
        seg_onoff_boton_bl.config(fg='red')
        seg_onoff_boton_bl['text'] = 'OFF'
    else:
        seg_onoff_bl = 1
        seg_onoff_boton_bl.config(fg='green')  
        seg_onoff_boton_bl['text'] = 'ON '		


def callback_control_intext(*args):
    global control_int_ext,flag
    if control_int_ext == 0:
        control_int_ext = 1
        control_intext_boton['text'] = 'EXT'
        flag = 1
    else:
        control_int_ext = 0
        control_intext_boton['text'] = 'INT'			

def callback_buscar(*args):
    global filename_path, filename_path_var
    filename_path = tkFileDialog.askdirectory(parent=root,title='Choose a directory')         
    filename_path_var.set(filename_path)


def callback_guardar(*args):
    global filename_path, filename_path_mon, file_mon, guardar_onoff, ind_arch
    
    if guardar_onoff == 1:
        guardar_onoff = 0
        button_guardar.config(fg='red')
        file_mon.close()
    else:
        guardar_onoff = 1
        button_guardar.config(fg='green')

        j = 0
        while 1:
            filename_path_mon = os.path.join(filename_path, 'MONITOREO_' + '%02d' % (j))
            if not os.path.isdir(filename_path_mon):
                break
            j = j + 1
        
        #filename_path_mon = os.path.join(filename_path, 'MONITOREO')
        button_guardar_var.set(filename_path_mon)
        os.mkdir(filename_path_mon)    
        ind_arch = 0
        inttostr = '%06d' % (ind_arch)
        file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w')    
        file_mon.write('hora, control_ext, frecuencia_laser[Hz], ancho_de_pulso[ns], tec_laser_onoff, temp_act_laser[C], temp_set_laser[C], temp_set_laser1[C], tec_bloque_onoff, temp_act_bloque[C], temp_set_bloque[C], temp_set_bloque1[C], temp_seguidor_bloque[C],  modo_seguidor_bloque, tension_laser_act[mV], tension_laser_set[mV], temp_amb1[C], corriente_tec_laser[mA], corriente_tec_bloque[mA] \n')

		
root = Tk.Tk()


label = Tk.Label(root).grid(column=0, row=0,columnspan=1)
fig=Figure(figsize=(1, 1), dpi=1)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

if control_int_ext == 1:
    control_intext_boton = Tk.Button(root, text="EXT", font = "Helvetica 16 bold", command=callback_control_intext)
else:
    control_intext_boton = Tk.Button(root, text="INT", font = "Helvetica 16 bold", command=callback_control_intext)
control_intext_boton.grid(column=3,row=0)
control_l=Tk.Label(root,text="Control: ", font = "Helvetica 18 bold",)
control_l.grid(column=0,row=0,sticky='W')
control_l=Tk.Label(root,text="ns", font = "Helvetica 18 bold",)

# PLot
frecuencia_var = Tk.StringVar()
frecuencia_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=frecuencia_var)
frecuencia_w.grid(column=1,row=1,sticky='W')
frecuencia_l=Tk.Label(root,text="Frecuencia: ", font = "Helvetica 18 bold",)
frecuencia_l.grid(column=0,row=1,sticky='W')
frecuencia_l=Tk.Label(root,text="Hz", font = "Helvetica 18 bold",)
frecuencia_l.grid(column=2,row=1,sticky='W')
frecuencia_var.set(laser_frecuencia)

ancho_de_pulso_var = Tk.StringVar()
ancho_de_pulso_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=ancho_de_pulso_var)
ancho_de_pulso_w.grid(column=1,row=2,sticky='W')
ancho_de_pulso_l=Tk.Label(root,text="Ancho de pulso: ", font = "Helvetica 18 bold",)
ancho_de_pulso_l.grid(column=0,row=2,sticky='W')
ancho_de_pulso_l=Tk.Label(root,text="ns", font = "Helvetica 18 bold",)
ancho_de_pulso_l.grid(column=2,row=2,sticky='W')
ancho_de_pulso_var.set(laser_duracion)

tension_laser_var = Tk.StringVar()
tension_laser_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=tension_laser_var)
tension_laser_w.grid(column=1,row=3,sticky='W')
tension_laser_l=Tk.Label(root,text=u"Tensión láser: ", font = "Helvetica 18 bold",)
tension_laser_l.grid(column=0,row=3,sticky='W')
tension_laser_l=Tk.Label(root,text="V", font = "Helvetica 18 bold",)
tension_laser_l.grid(column=2,row=3,sticky='W')
tension_laser_var.set(laser_tension)

laser_onoff_boton = Tk.Button(root, text="OFF", font = "Helvetica 16 bold", command=callback_laser_onoff)
laser_onoff_boton.grid(column=3,row=3)
laser_onoff_boton.config(fg='red')

temp_set_laser_var = Tk.StringVar()
temp_set_laser_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=temp_set_laser_var)
temp_set_laser_w.grid(column=1,row=4,sticky='W')
temp_set_laser_l=Tk.Label(root,text=u"Temperatura set láser: ", font = "Helvetica 18 bold",)
temp_set_laser_l.grid(column=0,row=4,sticky='W')
temp_set_laser_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_set_laser_l.grid(column=2,row=4,sticky='W')
temp_set_laser_var.set(temp_setpoint)

tec_onoff_boton = Tk.Button(root, text="OFF", font = "Helvetica 16 bold", command=callback_tec_onoff)
tec_onoff_boton.grid(column=3,row=4)
tec_onoff_boton.config(fg='red')

temp_set_bloque_var = Tk.StringVar()
temp_set_bloque_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=temp_set_bloque_var)
temp_set_bloque_w.grid(column=1,row=5,sticky='W')
temp_set_bloque_l=Tk.Label(root,text=u"Temperatura set bloque: ", font = "Helvetica 18 bold",)
temp_set_bloque_l.grid(column=0,row=5,sticky='W')
temp_set_bloque_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_set_bloque_l.grid(column=2,row=5,sticky='W')
temp_set_bloque_var.set(temp_setpoint_bl)

tec_onoff_boton_bl = Tk.Button(root, text="OFF", font = "Helvetica 16 bold", command=callback_tec_onoff_bl)
tec_onoff_boton_bl.grid(column=3,row=5)
tec_onoff_boton_bl.config(fg='red')


temp_seg_bloque_var = Tk.StringVar()
temp_seg_bloque_w = Tk.Entry(root, width=7, font = "Helvetica 18 bold", textvariable=temp_seg_bloque_var)
temp_seg_bloque_w.grid(column=1,row=6,sticky='W')
temp_seg_bloque_l=Tk.Label(root,text=u"Temperatura seguidor bloque: ", font = "Helvetica 18 bold",)
temp_seg_bloque_l.grid(column=0,row=6,sticky='W')
temp_seg_bloque_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_seg_bloque_l.grid(column=2,row=6,sticky='W')
temp_seg_bloque_var.set(temp_seguidor_bl)

seg_onoff_boton_bl = Tk.Button(root, text="OFF", font = "Helvetica 16 bold", command=callback_seg_onoff_bl)
seg_onoff_boton_bl.grid(column=3,row=6)
seg_onoff_boton_bl.config(fg='red')


temp_act_laser_var = Tk.StringVar()
temp_act_laser_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_act_laser_var)
temp_act_laser_w.grid(column=1,row=7,sticky='W')
temp_act_laser_l=Tk.Label(root,text=u"Temperatura actual láser: ", font = "Helvetica 18 bold",)
temp_act_laser_l.grid(column=0,row=7,sticky='W')
temp_act_laser_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_act_laser_l.grid(column=2,row=7,sticky='W')
temp_act_laser_var.set(0.0)

temp_set1_laser_var = Tk.StringVar()
temp_set1_laser_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_set1_laser_var)
temp_set1_laser_w.grid(column=3,row=7,sticky='W')
temp_set1_laser_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_set1_laser_l.grid(column=4,row=7,sticky='W')
temp_set1_laser_var.set(0.0)


temp_act_bloque_var = Tk.StringVar()
temp_act_bloque_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_act_bloque_var)
temp_act_bloque_w.grid(column=1,row=8,sticky='W')
temp_act_bloque_l=Tk.Label(root,text=u"Temperatura actual bloque: ", font = "Helvetica 18 bold",)
temp_act_bloque_l.grid(column=0,row=8,sticky='W')
temp_act_bloque_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_act_bloque_l.grid(column=2,row=8,sticky='W')
temp_act_bloque_var.set(0.0)

temp_set1_bloque_var = Tk.StringVar()
temp_set1_bloque_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_set1_bloque_var)
temp_set1_bloque_w.grid(column=3,row=8,sticky='W')
temp_set1_bloque_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_set1_bloque_l.grid(column=4,row=8,sticky='W')
temp_set1_bloque_var.set(0.0)

tension_act_laser_var = Tk.StringVar()
tension_act_laser_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=tension_act_laser_var)
tension_act_laser_w.grid(column=1,row=9,sticky='W')
tension_act_laser_l=Tk.Label(root,text=u"Tensión actual láser: ", font = "Helvetica 18 bold",)
tension_act_laser_l.grid(column=0,row=9,sticky='W')
tension_act_laser_l=Tk.Label(root,text="mV", font = "Helvetica 18 bold",)
tension_act_laser_l.grid(column=2,row=9,sticky='W')
tension_act_laser_var.set(0.0)


corr_laser_var = Tk.StringVar()
corr_laser_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=corr_laser_var)
corr_laser_w.grid(column=1,row=10,sticky='W')
corr_laser_l=Tk.Label(root,text=u"Corriente TEC láser: ", font = "Helvetica 18 bold",)
corr_laser_l.grid(column=0,row=10,sticky='W')
corr_laser_l=Tk.Label(root,text=" mA", font = "Helvetica 18 bold",)
corr_laser_l.grid(column=2,row=10,sticky='W')
corr_laser_var.set(0.0)

corr_bloque_var = Tk.StringVar()
corr_bloque_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=corr_bloque_var)
corr_bloque_w.grid(column=1,row=11,sticky='W')
corr_bloque_l=Tk.Label(root,text=u"Corriente TEC bloque: ", font = "Helvetica 18 bold",)
corr_bloque_l.grid(column=0,row=11,sticky='W')
corr_bloque_l=Tk.Label(root,text=" mA", font = "Helvetica 18 bold",)
corr_bloque_l.grid(column=2,row=11,sticky='W')
corr_bloque_var.set(0.0)

temp_amb1_var = Tk.StringVar()
temp_amb1_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_amb1_var)
temp_amb1_w.grid(column=1,row=12,sticky='W')
temp_amb1_l=Tk.Label(root,text=u"Temperatura ambiente1: ", font = "Helvetica 18 bold",)
temp_amb1_l.grid(column=0,row=12,sticky='W')
temp_amb1_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_amb1_l.grid(column=2,row=12,sticky='W')
temp_amb1_var.set(0.0)

temp_amb2_var = Tk.StringVar()
temp_amb2_w = Tk.Label(root, width=7, font = "Helvetica 18 bold", textvariable=temp_amb2_var)
temp_amb2_w.grid(column=1,row=13,sticky='W')
temp_amb2_l=Tk.Label(root,text=u"Temperatura ambiente2: ", font = "Helvetica 18 bold",)
temp_amb2_l.grid(column=0,row=13,sticky='W')
temp_amb2_l=Tk.Label(root,text="°C", font = "Helvetica 18 bold",)
temp_amb2_l.grid(column=2,row=13,sticky='W')
temp_amb2_var.set(0.0)

button_buscar = Tk.Button(root,text=u"Buscar", font = "Helvetica 16 bold", command=callback_buscar)
button_buscar.grid(column=0,row=14,sticky='W')    

filename_path_var = Tk.StringVar()
filename_path_w = Tk.Label(root, width=50, font = "Helvetica 10 bold", textvariable=filename_path_var)
filename_path_w.grid(column=0,row=16,columnspan=4,sticky='W')

button_guardar = Tk.Button(root,text=u"Guardar", font = "Helvetica 16 bold", command=callback_guardar)
button_guardar.grid(column=0,row=15,sticky='W')   
button_guardar.config(fg='red')

button_guardar_var = Tk.StringVar()
button_guardar_l=Tk.Label(root,font = "Helvetica 10 bold",textvariable=button_guardar_var)
button_guardar_l.grid(column=0,row=17,columnspan=4,sticky='W')


ani = animation.FuncAnimation(fig, updatefig2, interval=100, blit=False)
plt.show()
Tk.mainloop()


