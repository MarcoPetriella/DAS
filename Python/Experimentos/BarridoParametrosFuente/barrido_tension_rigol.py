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
import visa


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
temp_setpoint = 15
laser_duracion = 20
laser_tension = 1.02

tt = 0
ind_med = 0
ind_arch = 0
guardar_onoff = 1
file_mon = 0


rm = visa.ResourceManager()
# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
instruments = rm.list_resources()
usb = list(filter(lambda x: 'USB' in x, instruments))
if len(usb) != 1:
    print('Bad instrument list', instruments)
    sys.exit(-1)
    
power_supply = rm.open_resource(usb[0], timeout=20, chunk_size=1024000)

filename_path_mon = "D:\\Programas_C\\std_fft_osc_bandas_2.1\\bin\\Release\\Monitoreo"
os.mkdir(filename_path_mon)    
ind_arch = 0
inttostr = '%06d' % (ind_arch)
file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w')    
file_mon.write('hora, control_ext, frecuencia_laser[Hz], ancho_de_pulso[ns], tec_laser_onoff, temp_act_laser[C], temp_set_laser[C], temp_set_laser1[C], tec_bloque_onoff, temp_act_bloque[C], temp_set_bloque[C], temp_set_bloque1[C], temp_seguidor_bloque[C],  modo_seguidor_bloque, tension_laser_act[mV], tension_laser_set[mV], temp_amb1[C], corriente_tec_laser[mA], corriente_tec_bloque[mA] \n')

temp_setpoint_0 = 14.8
laser_tension_0 = 2.25
laser_duracion_0 = 100

delta_temp = 0.1
delta_tension = 0.01
delta_duracion = 100

flag_ini = 0

for i in range(30):    
    temp_setpoint = temp_setpoint_0 + i*delta_temp        
    flag_temp = 0
    
    for j in range(30):       
        laser_tension = laser_tension_0 + j*delta_tension
        flag_tension = 0  
        
        for k in range(1):   
            laser_duracion = laser_duracion_0 + k*delta_duracion 
            
            

            
            for m in range(3):
                arduino.write(struct.pack('<bfffiififi',0,laser_frecuencia,laser_duracion,laser_tension,int(laser_onoff),int(tec_onoff),temp_setpoint,int(tec_onoff_bl),temp_setpoint_bl,int(control_int_ext)))  
                arduino.flush()
                time.sleep(0.4) 
                
                
            if flag_ini == 0:
                time.sleep(2*60)                 
       
            if flag_temp == 0:
                time.sleep(1*60) 
                
            if flag_tension == 0:
                power_supply.write(":APPL CH2," + str(laser_tension) + ",0.1")
                time.sleep(5) 
            
            #time.sleep(5) 
            
            flag_ini = 1
            flag_temp = 1
            flag_tension = 1
            
            print temp_setpoint, laser_tension, laser_duracion
                
            tiempo_medicion = datetime.datetime.now()
            tiempo_actual = datetime.datetime.now()
            delta = tiempo_actual - tiempo_medicion
            delta_sec = delta.total_seconds()
            
            print arduino.inWaiting()
            while arduino.inWaiting() > 0:
                arduino.readline()            
            
            while(delta_sec < 1*30):

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
            
            
file_mon.close()
arduino.close()
power_supply.close()