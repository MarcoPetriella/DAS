# -*- coding: utf-8 -*-
"""
Created on Thu Aug 09 12:24:33 2018

@author: Marco
"""

from funciones_das import carga_datos_temperatura3
import numpy as np
import datetime 
import os
from funciones4 import header_read
from funciones4 import data_read
from funciones_das import carga_matriz_std
from funciones_das import carga_matriz_raw
from funciones_das import carga_matriz_avg
from funciones_das import carga_matriz_monitoreo
import matplotlib.pyplot as plt

import matplotlib.pylab as pylab
params = {'legend.fontsize': 16,
     #     'figure.figsize': (15, 5),
         'lines.markersize': 6,
         'axes.labelsize': 16,
         'axes.titlesize': 12,
         'xtick.labelsize': 16,
         'ytick.labelsize': 16}
pylab.rcParams.update(params)

parametros = {}
parametros['time_str'] = '18_18_08_01_42_19'
parametros['tiempo_ini'] = '2018-08-18 01:45:23'
parametros['tiempo_fin'] = '2018-08-18 21:36:14'
parametros['dt'] = {'names': ('fecha','control_ext', 'frecuencia_laser_hz', 'ancho_de_pulso_ns', 'tec_laser_onoff', 'temp_act_laser_c', 'temp_set_laser_c', 'temp_set_laser1_c', 'tec_bloque_onoff', 'temp_act_bloque_c','temp_set_bloque_c','temp_set_bloque1_c','temp_seguidor_bloque_c','modo_seguidor_bloque','tension_laser_act_mv','tension_laser_set_mv','temp_amb1_c','corriente_tec_laser_ma','corriente_tec_bloque_ma' ),'formats': ('S25','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4')}


matriz, vector_tiempo = carga_datos_temperatura3(parametros)




temp_setpoint_0 = 14.8
laser_tension_0 = 2.35
laser_duracion_0 = 100

delta_temp = 0.1
delta_tension = 0.01
delta_duracion = 100

dim1 = 30
dim2 = 30
dim3 = 2

tiempo_ini_matriz = np.zeros((dim1,dim2,dim3),dtype='int')
tiempo_fin_matriz = np.zeros((dim1,dim2,dim3),dtype='int')

temp_setpoint_m_ant = 0
laser_tension_m_ant = 0
laser_duracion_m_ant = 0

flag = np.zeros((dim1,dim2,dim3),dtype='int')
flag1 = 0

i_ant = 0
j_ant = 0
k_ant = 0

for m in range(len(matriz[0])):
    
    temp_setpoint_m = round(10*matriz[6][m])
    laser_tension_m =  round(matriz[15][m])
    laser_duracion_m = round(matriz[3][m])

    for i in range(dim1):
        temp_setpoint = temp_setpoint_0 + i*delta_temp     
        temp_setpoint = round(10*temp_setpoint)
        
        for j in range(dim2):
            laser_tension = laser_tension_0 + j*delta_tension   
            laser_tension = round(laser_tension*1000)
            
            for k in range(dim3):
                laser_duracion = round(laser_duracion_0 + k*delta_duracion)
                
                
                if temp_setpoint == temp_setpoint_m and laser_tension == laser_tension_m and laser_duracion == laser_duracion_m:   
                    
                    if flag[i][j][k] == 0:
                        flag[i][j][k] = 1  
                            
                        #print temp_setpoint, laser_tension, laser_duracion
                                                
                        tiempo_ini_matriz[i][j][k] = int(m)
                        if flag1 == 1:     
                            tiempo_fin_matriz[i_ant][j_ant][k_ant] = int(m-1 )   
                        flag1 = 1              

                        i_ant = i
                        j_ant = j
                        k_ant = k                                
                        




FrecLaser = 10000                
time_str = parametros['time_str']
ano = time_str[0:2]
ano = '20' + ano

dia = time_str[3:5]
mes = time_str[6:8]

hora = time_str[9:11]
minuto = time_str[12:14]
seg = time_str[15:17]

tiempo_0 = ano + '-' + mes + '-' + dia + ' ' + hora + ':' + minuto + ':' + seg
tiempo_0_date = datetime.datetime.strptime(tiempo_0, '%Y-%m-%d %H:%M:%S')


parametros_std = {}
parametros_std['time_str'] = parametros['time_str']
parametros_std['carpeta_std'] = 'STD'
nombre_header = os.path.join(parametros_std['time_str'], parametros_std['carpeta_std'], 'std.hdr')
nombre_archivo = os.path.join(parametros_std['time_str'], parametros_std['carpeta_std'], '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros_std['c'] = 299792458.
parametros_std['n'] = 1.51670026
parametros_std['offset_m'] = 0
parametros_std['FrecLaser'] = FrecLaser
parametros_std['c_f'] = parametros_std['c'] / parametros_std['n']
parametros_std['zoom_i_m'] = 800
parametros_std['zoom_f_m'] = 900


parametros_mon_laser = {}
parametros_mon_laser['time_str'] = parametros['time_str']
parametros_mon_laser['sub_dir'] = 'MON_LASER'
nombre_header = os.path.join(parametros_mon_laser['time_str'], parametros_mon_laser['sub_dir'], 'laser.mon.hdr')
nombre_archivo = os.path.join(parametros_mon_laser['time_str'], parametros_mon_laser['sub_dir'], '000000.mon')
header = header_read(nombre_header, nombre_archivo)
parametros_mon_laser['FrecLaser'] = FrecLaser

parametros_mon_edfa = {}
parametros_mon_edfa['time_str'] = parametros['time_str']
parametros_mon_edfa['sub_dir'] = 'MON_EDFA'
nombre_header = os.path.join(parametros_mon_edfa['time_str'], parametros_mon_edfa['sub_dir'], 'laser.mon.hdr')
nombre_archivo = os.path.join(parametros_mon_edfa['time_str'], parametros_mon_edfa['sub_dir'], '000000.mon')
header = header_read(nombre_header, nombre_archivo)
parametros_mon_edfa['FrecLaser'] = FrecLaser                     
                                    

parametros_mean = {}
parametros_mean['time_str'] = parametros['time_str']
parametros_mean['carpeta_std'] = 'MEAN'
nombre_header = os.path.join(parametros_mean['time_str'], parametros_mean['carpeta_std'], 'std.hdr')
nombre_archivo = os.path.join(parametros_mean['time_str'], parametros_mean['carpeta_std'], '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros_mean['c'] = 299792458.
parametros_mean['n'] = 1.51670026
parametros_mean['offset_m'] = 0
parametros_mean['FrecLaser'] = FrecLaser
parametros_mean['c_f'] = parametros_mean['c'] / parametros_mean['n']
parametros_mean['zoom_i_m'] = 200
parametros_mean['zoom_f_m'] = 800    
               
parametros_mean_1 = {}
parametros_mean_1['time_str'] = parametros['time_str']
parametros_mean_1['carpeta_std'] = 'MEAN'
nombre_header = os.path.join(parametros_mean_1['time_str'], parametros_mean_1['carpeta_std'], 'std.hdr')
nombre_archivo = os.path.join(parametros_mean_1['time_str'], parametros_mean_1['carpeta_std'], '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros_mean_1['c'] = 299792458.
parametros_mean_1['n'] = 1.51670026
parametros_mean_1['offset_m'] = 0
parametros_mean_1['FrecLaser'] = FrecLaser
parametros_mean_1['c_f'] = parametros_mean_1['c'] / parametros_mean_1['n']
parametros_mean_1['zoom_i_m'] = 100
parametros_mean_1['zoom_f_m'] = 900    
               
               
parametros_raw = {}
parametros_raw['time_str'] = parametros['time_str']
parametros_raw['carpeta_raw'] = 'RAW_CH0'
nombre_header = os.path.join(parametros_raw['time_str'], parametros_raw['carpeta_raw'], 'ch0.hdr')
nombre_archivo = os.path.join(parametros_raw['time_str'], parametros_raw['carpeta_raw'], '000000.bin')
header = header_read(nombre_header, nombre_archivo)
parametros_raw['c'] = 299792458.
parametros_raw['n'] = 1.46879964
parametros_raw['offset_m'] = 0
parametros_raw['FrecLaser'] = FrecLaser
parametros_raw['c_f'] = parametros_raw['c'] / parametros_raw['n']
parametros_raw['zoom_i_m'] = 0
parametros_raw['zoom_f_m'] = 5
parametros_raw['header_file'] = 'ch0.hdr'               
               
mon_laser_ijk = np.zeros((dim1,dim2,dim3))   
mon_edfa_ijk = np.zeros((dim1,dim2,dim3))      
mon_edfa_norm_ijk = np.zeros((dim1,dim2,dim3)) 
std_raw_norm_ijk = np.zeros((dim1,dim2,dim3))                         
std_raw_ijk = np.zeros((dim1,dim2,dim3))
std_ijk = np.zeros((dim1,dim2,dim3))
ruido_teo_apd_ijk = np.zeros((dim1,dim2,dim3))
sensi_ijk = np.zeros((dim1,dim2,dim3))
mean_laser_ijk = np.zeros((dim1,dim2,dim3))
mean_edfa_ijk = np.zeros((dim1,dim2,dim3))

temp_label = []
tension_label = []


## PARAMETROS APD
Resp = 0.90 # [A/W]
M = 10
tranimpedancia = 50000

Idg = 100*10**-12
Ids = 100*10**-12
q = 1.60*10**-19
Idark = M*Idg + Ids;
F = 5.5
Bw = 90*10**6
Kb = 1.38*10**-23
T = 298
Rsh = 10*10**6


# Calibracion fotodiodo
c_laser = 0.21
c_edfa = 21.
                    
for i in range(dim1):
    print i
    temp_setpoint = temp_setpoint_0 + i*delta_temp    
    temp_label.append(temp_setpoint)
        
    for j in range(dim2):
        laser_tension = laser_tension_0 + j*delta_tension 
        tension_label.append(laser_tension)
            
        for k in range(dim3):
            laser_duracion = laser_duracion_0 + k*delta_duracion
            
            
            ind_i = tiempo_ini_matriz[i][j][k]
            ind_f = tiempo_fin_matriz[i][j][k]
            
            tiempo_i = matriz[0][ind_i]
            tiempo_f = matriz[0][ind_f]
            
            tiempo_i = tiempo_i[0:19]
            tiempo_f = tiempo_f[0:19]
            
            tiempo_ini_date = datetime.datetime.strptime(tiempo_i, '%Y-%m-%d %H:%M:%S')
            tiempo_fin_date = datetime.datetime.strptime(tiempo_f, '%Y-%m-%d %H:%M:%S') 
            
            tiempo_ini_date = tiempo_ini_date + datetime.timedelta(0, 10) 
            tiempo_fin_date = tiempo_ini_date + datetime.timedelta(0, 20)             
            
            tiempo_ini = tiempo_ini_date.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_fin = tiempo_fin_date.strftime("%Y-%m-%d %H:%M:%S")
            
            parametros_std['tiempo_ini'] = tiempo_ini
            parametros_std['tiempo_fin'] = tiempo_fin
                          
            data, tiempo_filas_std, pos_bin, = carga_matriz_std(parametros_std)                       
            std_ijk[i][j][k] = np.mean(data)
            
#            if i == 11 and j == 12 and k == 0:
#                fig = plt.figure(figsize=(14, 7), dpi=250)
#                ax = fig.add_axes([.1, .1, .8, .8])
#                im = ax.imshow(data, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
#                fig.colorbar(im)                
            
            
            parametros_mean['tiempo_ini'] = tiempo_ini
            parametros_mean['tiempo_fin'] = tiempo_fin            
            
            data, tiempo_filas_mean, pos_bin, = carga_matriz_std(parametros_mean)           
            sensi_ijk[i][j][k] = np.std(data[10,:])/np.mean(data[10,:])

            parametros_mean_1['tiempo_ini'] = tiempo_ini
            parametros_mean_1['tiempo_fin'] = tiempo_fin     
            
            data1, tiempo_filas_mean, pos_bin, = carga_matriz_std(parametros_mean_1)                       

            parametros_raw['tiempo_ini'] = tiempo_ini
            parametros_raw['tiempo_fin'] = tiempo_fin            
            
            data_raw, tiempo_filas_raw, pos_bin, = carga_matriz_raw(parametros_raw)           
            std_raw_ijk[i][j][k] = np.mean(np.std(data_raw[0:FrecLaser,:],0)/np.mean(data_raw[0:FrecLaser,:],0))
            
            parametros_mon_laser['tiempo_ini'] = tiempo_ini
            parametros_mon_laser['tiempo_fin'] = tiempo_fin             
            
            data_laser, tiempo_filas_mon = carga_matriz_monitoreo(parametros_mon_laser)
            mon_laser_ijk[i][j][k] = np.std(data_laser[0,0:FrecLaser])/np.mean(data_laser[0,0:FrecLaser])
            
            mean_laser_ijk[i][j][k] = np.mean(data_laser[0,0:FrecLaser])

            parametros_mon_edfa['tiempo_ini'] = tiempo_ini
            parametros_mon_edfa['tiempo_fin'] = tiempo_fin             
            
            data_edfa, tiempo_filas_mon = carga_matriz_monitoreo(parametros_mon_edfa)
            mon_edfa_ijk[i][j][k] = np.std(data_edfa[0,0:FrecLaser])/np.mean(data_edfa[0,0:FrecLaser])
            
            mean_edfa_ijk[i][j][k] = np.mean(data_edfa[0,0:FrecLaser])
            
            data_norm = data_edfa[0,0:FrecLaser]/data_laser[0,0:FrecLaser]
            mon_edfa_norm_ijk[i][j][k] = np.std(data_norm)/np.mean(data_norm)
                        
            data_raw_norm = np.transpose(data_raw[0:FrecLaser,:])/data_edfa[0,0:FrecLaser]
            std_raw_norm_ijk[i][j][k] = np.mean(np.std(data_raw_norm, axis=1)/np.mean(data_raw_norm, axis=1))
            
            # Ruido teorico apd
            data_raw_v = data_raw[0:FrecLaser,5]/2**14
            data_raw_v_mean = np.mean(data_raw_v)            
            Iph = data_raw_v_mean/tranimpedancia
            P = Iph/M/Resp
            Imed = Idark + Iph            
            eph = np.sqrt(2*q*(Ids + (abs(Idg)*M*M + M*abs(Iph))*F)*Bw)            
            ethermal = np.sqrt(4*Kb*T*Bw/Rsh);
            sumi = np.sqrt(eph*eph + ethermal*ethermal);
            snr_teo = (Imed/sumi)
            
            ruido_teo_apd_ijk[i][j][k] = 1/snr_teo
            
            


            
for k in range(dim3):
    laser_duracion = laser_duracion_0 + k*delta_duracion
    
    os.mkdir(str(laser_duracion)) 
            
    std_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            std_ij[i][j] = std_ijk[i][j][k]
            
            
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(std_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.1])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido filtrado en función de la tensión láser y temperatura del láser. Señal normalizada por energia edfa. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD/MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'RuidoFiltrado_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    ##
    std_raw_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            std_raw_ij[i][j] = std_raw_ijk[i][j][k]
            
            
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(std_raw_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.4])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Ruido_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    ##
    std_raw_norm_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            std_raw_norm_ij[i][j] = std_raw_norm_ijk[i][j][k]
            
            
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(std_raw_norm_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.4])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido en función de la tensión láser y temperatura del láser. Señal normalizada por energia edfa. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Ruido_normalizado_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##
    ruido_teo_apd_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            ruido_teo_apd_ij[i][j] = ruido_teo_apd_ijk[i][j][k]
            
            
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(ruido_teo_apd_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.4])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido teórico APD en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Ruido_teorico_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##
    ruido_teo_raw_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            ruido_teo_raw_ij[i][j] = std_raw_norm_ijk[i][j][0]/ruido_teo_apd_ijk[i][j][k]
            
            
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(ruido_teo_raw_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([1,5])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido medido / teórico APD en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label(u'Medido / Teórico', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Ruido_teorico_medido_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##       
    sensi_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            sensi_ij[i][j] = sensi_ijk[i][j][k]        
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(sensi_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.5])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Sensibilidad en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('Sensibilidad', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Sensibilidad_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##       
    coc_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            coc_ij[i][j] = sensi_ijk[i][j][k]/std_raw_ijk[i][j][k]        
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(coc_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,12])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Sensibilidad/Ruido en función de la tensión láser y temperatura del láser. Señal normalizada por energia edfa. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('Sensibilidad / Ruido', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Sensibilidad_ruido_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##       
    mon_laser_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            mon_laser_ij[i][j] = mon_laser_ijk[i][j][k]      
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(mon_laser_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.15])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido de la energía láser en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Laser_ruido_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    
    ##       
    mon_edfa_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            mon_edfa_ij[i][j] = mon_edfa_ijk[i][j][k]      
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(mon_edfa_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.15])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido de la energía edfa en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Edfa_ruido_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    
    ##       
    mon_edfa_norm_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            mon_edfa_norm_ij[i][j] = mon_edfa_norm_ijk[i][j][k]      
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(mon_edfa_norm_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    im.set_clim([0,0.15])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ruido de la energía edfa normalizada en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label('STD / MEAN', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Edfa_ruido_norm_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    
    ##       
    mean_laser_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            mean_laser_ij[i][j] = mean_laser_ijk[i][j][k]/2**15*c_laser*100e-9      
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(mean_laser_ij*1e9, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Enegía pulso laser en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label(u'Energía Láser [nJ]', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Energia_laser_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##       
    mean_edfa_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            mean_edfa_ij[i][j] = mean_edfa_ijk[i][j][k]/2**15*c_edfa*100e-9      
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(mean_edfa_ij*1e6, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Enegía pulso edfa en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label(u'Energía Edfa [uJ]', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Energia_edfa_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 
    
    
    ##       
    ganancia_ij = np.zeros((dim1,dim2))
    for i in range(dim1):
        for j in range(dim2):
            ganancia_ij[i][j] = (mean_edfa_ijk[i][j][k]*c_edfa)/(mean_laser_ijk[i][j][0]*c_laser)
    
    fig = plt.figure(figsize=(14, 7), dpi=250)
    ax = fig.add_axes([.1, .1, .8, .8])
    im = ax.imshow(ganancia_ij, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
    ax.set_xlim([-0.50,dim2-1+0.5])
    ax.set_ylim([-0.50,dim1-1+0.5])
    xt = ax.get_xticks()
    ax.set_xticklabels(laser_tension_0 + np.asarray(xt)*delta_tension)
    yt = ax.get_yticks()
    ax.set_yticklabels(temp_setpoint_0 + np.asarray(yt)*delta_temp)
    ax.set_xlabel(u'Tensión [V]')
    ax.set_ylabel(u'Temperatura láser [°C]')
    ax.set_title(u'Ganancia del edfa en energía en función de la tensión láser y temperatura del láser. Ancho de pulso de ' + str(laser_duracion) +  ' ns')
    cbar = fig.colorbar(im)
    cbar.set_label(u'Ganancia', rotation=270, labelpad=40)
    fig.savefig(os.path.join(str(laser_duracion),'Ganancia_' + str(laser_duracion) +  'ns.png'), dpi=300)
    plt.close(fig) 



plt.plot(mean_laser_ij[:],mean_edfa_ij[:])


[y,x] = np.histogram(data,range=(0,100),bins=30)

x = x[:len(x)-1:]

        
fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.1, .1, .8, .8])
ax.bar(x,y)




i = 20
j = 22
k = 0

ind_i = tiempo_ini_matriz[i][j][k]
ind_f = tiempo_fin_matriz[i][j][k]
            
tiempo_i = matriz[0][ind_i]
tiempo_f = matriz[0][ind_f]
            
tiempo_i = tiempo_i[0:19]
tiempo_f = tiempo_f[0:19]
            
tiempo_ini_date = datetime.datetime.strptime(tiempo_i, '%Y-%m-%d %H:%M:%S')
tiempo_fin_date = datetime.datetime.strptime(tiempo_f, '%Y-%m-%d %H:%M:%S') 
            
tiempo_ini_date = tiempo_ini_date + datetime.timedelta(0, -10) 
tiempo_fin_date = tiempo_ini_date + datetime.timedelta(0, 50)             
            
tiempo_ini = tiempo_ini_date.strftime("%Y-%m-%d %H:%M:%S")
tiempo_fin = tiempo_fin_date.strftime("%Y-%m-%d %H:%M:%S")
            
parametros_std['tiempo_ini'] = tiempo_ini
parametros_std['tiempo_fin'] = tiempo_fin
parametros_std['zoom_i_m'] = 0
parametros_std['zoom_f_m'] = 1100

time_str = parametros_std['time_str']
ano = time_str[0:2]
ano = '20' + ano
dia = time_str[3:5]
mes = time_str[6:8]
hora = time_str[9:11]
minuto = time_str[12:14]
seg = time_str[15:17]
tiempo_0 = ano + '-' + mes + '-' + dia + ' ' + hora + ':' + minuto + ':' + seg
tiempo_0_date = datetime.datetime.strptime(tiempo_0, '%Y-%m-%d %H:%M:%S')

data, tiempo_filas_std, pos_bin, = carga_matriz_std(parametros_std)                       
std_ijk[i][j][k] = np.mean(data)
            
fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.1, .1, .8, .8])
im = ax.imshow(data, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
fig.colorbar(im)    


#######################
#parametros_std = {}
#parametros_std['time_str'] = parametros['time_str']
#parametros_std['carpeta_std'] = 'STD'
#nombre_header = os.path.join(parametros_std['time_str'], parametros_std['carpeta_std'], 'std.hdr')
#nombre_archivo = os.path.join(parametros_std['time_str'], parametros_std['carpeta_std'], '000000.std')
#header = header_read(nombre_header, nombre_archivo)
#parametros_std['c'] = 299792458.
#parametros_std['n'] = 1.51670026
#parametros_std['offset_m'] = 0
#parametros_std['FrecLaser'] = 10000
#parametros_std['c_f'] = parametros_std['c'] / parametros_std['n']
#parametros_std['zoom_i_m'] = 800
#parametros_std['zoom_f_m'] = 900
#
#i = 10
#j = 1
#k = 0              
#ind_i = tiempo_ini_matriz[i][j][k]
#ind_f = tiempo_fin_matriz[i][j][k]
#            
#tiempo_i = matriz[0][ind_i]
#tiempo_f = matriz[0][ind_f]
#
#tiempo_i = tiempo_i[0:19]
#tiempo_f = tiempo_f[0:19]
#
#tiempo_ini_date = datetime.datetime.strptime(tiempo_i, '%Y-%m-%d %H:%M:%S')
#tiempo_fin_date = datetime.datetime.strptime(tiempo_f, '%Y-%m-%d %H:%M:%S') 
#            
#tiempo_ini_date = tiempo_ini_date + datetime.timedelta(0, 10) 
#tiempo_fin_date = tiempo_ini_date + datetime.timedelta(0, 20)             
#            
#tiempo_ini = tiempo_ini_date.strftime("%Y-%m-%d %H:%M:%S")
#tiempo_fin = tiempo_fin_date.strftime("%Y-%m-%d %H:%M:%S")
#
#parametros_std['tiempo_ini'] = tiempo_ini
#parametros_std['tiempo_fin'] = tiempo_fin
#                          
#data, tiempo_filas_std, pos_bin, = carga_matriz_std(parametros_std)    
#
#fig = plt.figure(figsize=(14, 7), dpi=250)
#ax = fig.add_axes([.1, .1, .8, .8])
#im = ax.imshow(data, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
#                   
#std_ijk[i][j][k] = np.mean(data)

            
#            if i == 1 and j == 5 and k == 1:
#                plt.imshow(data, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')

              
            
            
            
#            tiempo_ini_date = datetime.datetime.strptime(tiempo_ini, '%Y-%m-%d %H:%M:%S')
#            tiempo_fin_date = datetime.datetime.strptime(tiempo_fin, '%Y-%m-%d %H:%M:%S')            
#            
#            dif_time_date_ini = tiempo_ini_date - tiempo_0_date
#            dif_time_date_fin = tiempo_fin_date - tiempo_0_date
#            dif_time_date_ini_sec = dif_time_date_ini.total_seconds()
#            dif_time_date_fin_sec = dif_time_date_fin.total_seconds()   
#            
#            header_path = os.path.join(time_str, 'RAW_CH0', 'ch0.hdr')
#            file_path = os.path.join(time_str, 'RAW_CH0', '000000.bin')
#            header = header_read(header_path, file_path)
#        
#            delta_t = header['FreqRatio'] * 5e-9
#            delta_x = c_f * delta_t / 2
#            zoom_i = int((zoom_i_m - offset_m) / delta_x)
#            zoom_f = int((zoom_f_m - offset_m) / delta_x)
#            vec_cols = np.array([zoom_i, zoom_f], dtype=np.uint64)
#        
#            nShotsChk = header['nShotsChk']
#            sec_per_fila = 1 / float(FrecLaser)
#            filas = header['Fils']
#            sec_per_file = filas * sec_per_fila            
#            
#            
#            ini_file = int(dif_time_date_ini_sec / sec_per_file)
#            ini_fila = dif_time_date_ini_sec % sec_per_file / sec_per_fila
#            fin_file = int(dif_time_date_fin_sec / sec_per_file)
#            fin_fila = dif_time_date_fin_sec % sec_per_file / sec_per_fila            
#            
#            filas_tot = int(dif_time_sec / sec_per_fila)
#            cols = int(vec_cols[1] - vec_cols[0] + 1)
#        
#            data = np.zeros([filas_tot, cols])
#            ind_fila = 0
#            print 'Cargando Dato Crudo: '
#            for i in range(ini_file, fin_file + 1):
#                file_num = '%06d' % (i)
#                file_i_path = os.path.join(time_str, 'RAW_CH0', file_num + '.bin')
#                header = header_read(header_path, file_i_path)
#        
#                if (ini_file == fin_file):
#                    vec_fils = np.array([ini_fila, fin_fila - 1])
#                else:
#                    if (i == ini_file):
#                        vec_fils = np.array([ini_fila, header['Fils'] - 1])
#                    elif (i == fin_file):
#                        vec_fils = np.array([0, fin_fila - 1])
#                    else:
#                        vec_fils = np.array([0, header['Fils'] - 1])
#        
#                header, vector = data_read(header_path, file_i_path, vec_fils, vec_cols)
#        
#                fila = vector.shape[0]
#                data[ind_fila: ind_fila + fila, :] = vector
#                ind_fila = ind_fila + fila