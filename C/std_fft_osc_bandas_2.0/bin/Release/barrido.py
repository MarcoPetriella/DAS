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
control_int_ext = 1
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

# parametros iniciales
laser_frecuencia = 10000
temp_setpoint_bl = 20
tec_onoff = 0
tec_onoff_bl = 0
control_int_ext = 1
laser_onoff = 0
temp_setpoint = 14.8
laser_duracion = 20
laser_tension = 1.00

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


start = datetime.datetime.now()
tt = 0
ind_med = 0
ind_arch = 0
guardar_onoff = 1
file_mon = 0

filename_path_mon = "D:\\Programas_C\\std_fft_osc_bandas_2.0\\bin\\Release\\Monitoreo1"
os.mkdir(filename_path_mon)    
ind_arch = 0
inttostr = '%06d' % (ind_arch)
file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w')    
file_mon.write('hora, control_ext, frecuencia_laser[Hz], ancho_de_pulso[ns], tec_laser_onoff, temp_act_laser[C], temp_set_laser[C], temp_set_laser1[C], tec_bloque_onoff, temp_act_bloque[C], temp_set_bloque[C], temp_set_bloque1[C], temp_seguidor_bloque[C],  modo_seguidor_bloque, tension_laser_act[mV], tension_laser_set[mV], temp_amb1[C], corriente_tec_laser[mA], corriente_tec_bloque[mA] \n')


for i in range(10):
    
    temp_setpoint = temp_setpoint + 0.2 
    arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))  
    time.sleep(2*60)
    print i
    
    laser_tension = 1.0
    for j in range(15):
        
        laser_tension = laser_tension + 0.02 
        arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))  
        time.sleep(20) 
        print j
        
        laser_duracion = 20
        for k in range(10):
            time.sleep(20) 
            print k
    
            laser_duracion = laser_duracion + 20 
            arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))  
           
            tiempo_medicion = datetime.datetime.now()
            tiempo_actual = datetime.datetime.now()
            delta = tiempo_actual - tiempo_medicion
            delta_sec = delta.total_seconds()
            
            while(delta_sec < 1*60):

                tiempo_actual = datetime.datetime.now()
                delta = tiempo_actual - tiempo_medicion
                delta_sec = delta.total_seconds()                
        
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


            print data_string2 