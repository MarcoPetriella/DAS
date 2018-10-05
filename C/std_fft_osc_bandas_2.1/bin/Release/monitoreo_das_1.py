# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 12:02:22 2017

@author: Marco
"""

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import Tkinter as Tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.pyplot import text

# from multiprocessing import Process
# from timeit import default_timer as timer
import datetime
from funciones4 import header_read
from funciones4 import data_read
import os
from scipy import signal
import sys


from funciones_das import carga_datos_temperatura
from funciones_das import carga_matriz_monitoreo
from funciones_das import carga_matriz_std



Writer = animation.writers['ffmpeg']
writer = Writer(fps=7, metadata=dict(artist='Marco'), bitrate=-1)


time_str = '18_07_03_17_56_07'
tiempo_ini = '2018-03-07 17:58:00'
tiempo_fin = '2018-03-08 16:35:00'
temp_file = '2018_03_07_17_55_59_val.txt'

#time_str = '18_07_03_17_56_07'
#tiempo_ini = '2018-03-08 17:05:00'
#tiempo_fin = '2018-03-09 09:00:00'
#temp_file = '2018_03_08_17_04_56_val.txt'

FrecLaser = 5000
c = 299792458.
n = 1.46879964
c_f = c/n
zoom_i_m_1 = 6000
zoom_f_m_1 = 8000
zoom_i_m_2 = 100
zoom_f_m_2 = 400


step_seg = 100 #segundos
filas_seg = 1.5*3600 #segundos
offset_m = 0
bins_hist = 200
bins_conv = 50;

output_movie = os.path.join(time_str, 'STD', 'peli_monitoreo2.mp4')
header_path = os.path.join(time_str, 'STD', 'std.hdr')

# Lista los archivos del directorio y se queda con el .std mas grande
for file in sorted(os.listdir(os.path.join(time_str, 'STD')), reverse=True):
    print file
    if file.endswith(".std"):
        path_last_file = os.path.join(time_str, 'STD', file)
        last_file = int(file[:-4])
        break

# Lista los archivos del directorio y se queda con el .std mas chico (eg. 000000.std)
for file in sorted(os.listdir(os.path.join(time_str, 'STD')), reverse=False):
    print file
    if file.endswith(".std"):
        path_first_file = os.path.join(time_str, 'STD', file)
        break


# Abro el header tomando el last_file para ver su tamano en filas
header = header_read(header_path, path_last_file)
delta_t = header['FreqRatio'] * 5e-9
delta_x = c_f * delta_t / 2
filas_last_file = header['Fils']

# Abro el header tomando el first_file para ver como se ve un archivo completo
header = header_read(header_path, path_first_file)
filas_0 = header['Fils']
nShotsChk = header['nShotsChk']

sec_per_fila = nShotsChk / FrecLaser
sec_per_file = filas_0 * sec_per_fila

step = int(step_seg/sec_per_fila)
filas = int(filas_seg/sec_per_fila)

ano = time_str[0:2]
ano = '20' + ano
dia = time_str[3:5]
mes = time_str[6:8]
hora = time_str[9:11]
minuto = time_str[12:14]
seg = time_str[15:17]

# este paso lo hace porque el programa guarda la carpeta como ano + dia + mes en lugar de ano + mes + dia
tiempo_0 = ano + '-' + mes + '-' + dia + ' ' + hora + ':' + minuto + ':' + seg
tiempo_0_date = datetime.datetime.strptime(tiempo_0, '%Y-%m-%d %H:%M:%S')
if tiempo_ini == '':
    tiempo_ini_date = tiempo_0_date
else:
    tiempo_ini_date = datetime.datetime.strptime(tiempo_ini, '%Y-%m-%d %H:%M:%S')

if tiempo_fin == '':
    # le agrego a tiempo_0_date la cantidad de archivos*sec_per_file. Le resto 1 segundo para que no se pase.
    tiempo_fin_date = tiempo_0_date + datetime.timedelta(0, (last_file) * sec_per_file + filas_last_file * sec_per_fila - 1)  # agrega segundos a datetime como: timedelta(days, seconds, then other fields).
else:
    tiempo_fin_date = datetime.datetime.strptime(tiempo_fin, '%Y-%m-%d %H:%M:%S')
        
    
tiempo_actual = tiempo_ini_date
dif_time_date_ini = tiempo_ini_date - tiempo_0_date
dif_time_date_fin = tiempo_fin_date - tiempo_0_date
dif_time_date_ini_sec = dif_time_date_ini.total_seconds()
dif_time_date_fin_sec = dif_time_date_fin.total_seconds()
dif_time_sec = dif_time_date_fin_sec - dif_time_date_ini_sec

ini_file = int(dif_time_date_ini_sec / sec_per_file)
ini_fila = (dif_time_date_ini_sec % sec_per_file) / sec_per_fila
# Hago que ini_fila sea multiplo del step
ini_fila = filas_0 - np.ceil((filas_0 - ini_fila) / step) * step  # redondeo para que ini_fila sea divisor entero de filas_0
fin_file = int(dif_time_date_fin_sec / sec_per_file)
fin_fila = (dif_time_date_fin_sec % sec_per_file) / sec_per_fila
# Hago que fin_fila sea multiplo del step
fin_fila = filas_0 - np.floor((filas_0 - fin_fila) / step) * step

zoom_i_1 = int((zoom_i_m_1 - offset_m) / delta_x)
zoom_f_1 = int((zoom_f_m_1 - offset_m) / delta_x)
zoom_i_2 = int((zoom_i_m_2 - offset_m) / delta_x)
zoom_f_2 = int((zoom_f_m_2 - offset_m) / delta_x)
                             
frames_tot = int((((fin_file - ini_file + 1) * filas_0 - (ini_fila) - (filas_0 - fin_fila)) / step))

vec_cols = np.array([0, header['Cols'] - 1], dtype=np.uint64)
cols_to_read = vec_cols[1] - vec_cols[0] + 1

parametros_std_1 = {}
parametros_std_1['time_str'] = time_str
parametros_std_1['c'] = c
parametros_std_1['n'] = n
parametros_std_1['offset_m'] = offset_m
parametros_std_1['FrecLaser'] = FrecLaser
parametros_std_1['c_f'] = parametros_std_1['c'] / parametros_std_1['n']
parametros_std_1['zoom_i_m'] = zoom_i_m_1
parametros_std_1['zoom_f_m'] = zoom_f_m_1              

parametros_std_2 = {}
parametros_std_2['time_str'] = time_str
parametros_std_2['c'] = c
parametros_std_2['n'] = n
parametros_std_2['offset_m'] = offset_m
parametros_std_2['FrecLaser'] = FrecLaser
parametros_std_2['c_f'] = parametros_std_1['c'] / parametros_std_1['n']
parametros_std_2['zoom_i_m'] = zoom_i_m_2
parametros_std_2['zoom_f_m'] = zoom_f_m_2                   
                              
parametros_mon_laser = {}
parametros_mon_laser['time_str'] = time_str
parametros_mon_laser['sub_dir'] = 'MON_LASER'
parametros_mon_laser['FrecLaser'] = 5000

parametros_mon_edfa = {}
parametros_mon_edfa['time_str'] = time_str
parametros_mon_edfa['sub_dir'] = 'MON_EDFA'
parametros_mon_edfa['FrecLaser'] = 5000
              
parametros_temp = {}
parametros_temp['file_name'] = temp_file
parametros_temp['tiempo_ini'] = tiempo_ini
parametros_temp['tiempo_fin'] = tiempo_fin
                  
tiempo_fin_j = tiempo_ini
     

std_mean_1 = []     
std_mean_2 = []
std_time = []    
       
vec_ruido_mon_laser = []
vec_ruido_mon_edfa = []
vec_mon_laser = []
vec_mon_edfa = []
mon_time = []


temp_amb_laser = []
temp_amb_edfa = []
temp_amb_compu = []
temp_time = []
       

matriz_temp,tiempo_temp = carga_datos_temperatura(parametros_temp)
ind_i = 0
inf_f = 0


parametros_mon_laser_i = parametros_mon_laser
parametros_mon_edfa_i = parametros_mon_edfa
parametros_mon_laser_i['tiempo_ini'] = tiempo_ini
parametros_mon_edfa_i['tiempo_ini'] = tiempo_ini
tiempo_fin_i = datetime.datetime.strptime(parametros_mon_laser_i['tiempo_ini'], '%Y-%m-%d %H:%M:%S')  + datetime.timedelta(seconds=step_seg)
tiempo_fin_i = tiempo_fin_i.strftime("%Y-%m-%d %H:%M:%S")
parametros_mon_laser_i['tiempo_fin'] = tiempo_fin_i
parametros_mon_edfa_i['tiempo_fin'] = tiempo_fin_i

matriz_mon_laser, tiempo_filas_mon_laser = carga_matriz_monitoreo(parametros_mon_laser_i)      
matriz_mon_edfa, tiempo_filas_mon_edfa = carga_matriz_monitoreo(parametros_mon_edfa_i)  

norm_laser_i = np.mean(matriz_mon_laser)
norm_edfa_i = np.mean(matriz_mon_edfa)


y_hist_edfa_acc = np.zeros(bins_hist)
y_hist_laser_acc = np.zeros(bins_hist)


t_tec = []

diff_bloque_acc = []
diff_laser_acc = []
diff_cor_bloque_acc = []
diff_cor_laser_acc = []  

norm_cor_bloque = 0
norm_cor_laser = 0  

def updatefig(j):
    global tiempo_fin_j, std_mean_1, std_mean_2, std_time, vec_ruido_mon_laser, vec_ruido_mon_edfa, mon_time, vec_mon_laser, vec_mon_edfa, temp_time, temp_amb_laser, temp_amb_edfa, temp_amb_compu, ind_i, ind_f, y_hist_edfa_acc, y_hist_laser_acc
    global t_tec
    global diff_bloque_acc, diff_laser_acc
    global diff_cor_bloque_acc, diff_cor_laser_acc
    global norm_cor_bloque, norm_cor_laser

    print float(j)/frames_tot*100.
    #print 'hola'
    
    tiempo_ini_j = tiempo_fin_j
    tiempo_fin_j_d = datetime.datetime.strptime(tiempo_ini_j, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=step_seg)
    tiempo_fin_j = tiempo_fin_j_d.strftime("%Y-%m-%d %H:%M:%S") 

    parametros_std_1['tiempo_ini'] = tiempo_ini_j
    parametros_std_1['tiempo_fin'] = tiempo_fin_j
                 
    parametros_std_2['tiempo_ini'] = tiempo_ini_j
    parametros_std_2['tiempo_fin'] = tiempo_fin_j                  

    parametros_mon_laser['tiempo_ini'] = tiempo_ini_j
    parametros_mon_laser['tiempo_fin'] = tiempo_fin_j
                  
    parametros_mon_edfa['tiempo_ini'] = tiempo_ini_j
    parametros_mon_edfa['tiempo_fin'] = tiempo_fin_j
                  
                
    matriz_std_1, tiempo_filas_std, pos_bin_std_1, = carga_matriz_std(parametros_std_1)         
    matriz_std_2, tiempo_filas_std, pos_bin_std_2, = carga_matriz_std(parametros_std_2)       
    matriz_mon_laser, tiempo_filas_mon_laser = carga_matriz_monitoreo(parametros_mon_laser)      
    matriz_mon_edfa, tiempo_filas_mon_edfa = carga_matriz_monitoreo(parametros_mon_edfa)  
    #matriz_temp,tiempo_temp = carga_datos_temperatura(parametros_temp)
        
    for i,t in enumerate(tiempo_temp):
        if (t > datetime.datetime.strptime(tiempo_fin_j,'%Y-%m-%d %H:%M:%S')):
            ind_f = i
            break
        
    x_std_1 = np.mean(matriz_std_1,axis = 1)   
    std_mean_1 = np.append(std_mean_1,x_std_1)  
    x_std_2 = np.mean(matriz_std_2,axis = 1)   
    std_mean_2 = np.append(std_mean_2,x_std_2)      
    
    std_time.extend(tiempo_filas_std)     
    delta_t = std_time[len(std_time)-1] - std_time[0]
    delta_t = delta_t.total_seconds()
    
    if (delta_t >= filas_seg):
        std_time = std_time[len(tiempo_filas_std):len(std_time)]
        std_mean_1 = std_mean_1[len(tiempo_filas_std):len(std_mean_1)]
        std_mean_2 = std_mean_2[len(tiempo_filas_std):len(std_mean_2)]


    vec_ruido_mon_laser = np.append(vec_ruido_mon_laser,np.std(matriz_mon_laser,axis=1)/np.mean(matriz_mon_laser,axis=1))
    vec_ruido_mon_edfa = np.append(vec_ruido_mon_edfa,np.std(matriz_mon_edfa,axis=1)/np.mean(matriz_mon_edfa,axis=1))
    vec_mon_laser = np.append(vec_mon_laser,np.mean(matriz_mon_laser,axis=1)/norm_laser_i)
    vec_mon_edfa = np.append(vec_mon_edfa,np.mean(matriz_mon_edfa,axis=1)/norm_edfa_i)

    mon_time.extend(tiempo_filas_mon_laser)  

    delta_t = mon_time[len(mon_time)-1] - mon_time[0]
    delta_t = delta_t.total_seconds()    
    
    if (delta_t >= filas_seg):
        mon_time = mon_time[len(tiempo_filas_mon_laser):len(mon_time)]
        vec_ruido_mon_laser = vec_ruido_mon_laser[len(tiempo_filas_mon_laser):len(vec_ruido_mon_laser)]
        vec_ruido_mon_edfa = vec_ruido_mon_edfa[len(tiempo_filas_mon_edfa):len(vec_ruido_mon_edfa)]
        vec_mon_laser = vec_mon_laser[len(tiempo_filas_mon_laser):len(vec_mon_laser)]
        vec_mon_edfa = vec_mon_edfa[len(tiempo_filas_mon_edfa):len(vec_mon_edfa)]

    
    ax.cla()
    ax0.cla()
    ax.plot(std_time,std_mean_1,'r',alpha=0.5,label='std waterfall 1')
    ax.plot(std_time,std_mean_2,'y',alpha=0.5,label='std waterfall 2')
    ax.plot(mon_time,vec_ruido_mon_laser,'b',alpha=0.7,label='std laser')
    ax.plot(mon_time,vec_ruido_mon_edfa,'g',alpha=0.7,label='std edfa')

    ax0.plot(mon_time,vec_mon_laser,'--b',alpha=0.5,label='medio laser')
    ax0.plot(mon_time,vec_mon_edfa,'--g',alpha=0.5,label='medio edfa')
    
    ax.set_ylim([0,0.1])
    ax0.set_ylim([0.65,1.15])
    ax.legend(loc='upper left')
    ax0.legend(loc='upper right')
    
    ax.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    ax0.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    
    std_time_t = []
    std_time_str = []
    for i in range(5):
        fe = std_time[int(0.25*i*(len(std_time)-1))]
        
        std_time_t.append(fe)
        std_time_str.append(fe.strftime("%H:%M:%S"))
            
    ax.set_xticks(std_time_t)
    ax.set_xticklabels(std_time_str)
    ax.set_title('Monitoreo de Laser-EDFA')
    ax.set_ylabel('Ruido Normalizado')
    ax0.set_ylabel('Energia Normalizada')   
    ax.set_xlabel('Tiempo')
    
    #########################################
    t_laser = matriz_temp[8][ind_i:ind_f]
    t_edfa = matriz_temp[7][ind_i:ind_f]
    t_compu = matriz_temp[9][ind_i:ind_f]
    t_t = tiempo_temp[ind_i:ind_f]
    
    temp_amb_laser.extend(t_laser) 
    temp_amb_edfa.extend(t_edfa) 
    temp_amb_compu.extend(t_compu) 
    temp_time.extend(t_t)  
        
    delta_t = temp_time[len(temp_time)-1] - temp_time[0]
    delta_t = delta_t.total_seconds()   

    if (delta_t >= filas_seg):
        temp_time = temp_time[len(t_t):len(temp_time)]
        temp_amb_laser = temp_amb_laser[len(t_laser):len(temp_amb_laser)]
        temp_amb_edfa = temp_amb_edfa[len(t_edfa):len(temp_amb_edfa)]
        temp_amb_compu = temp_amb_compu[len(t_compu):len(temp_amb_compu)]
        

    ax1.cla()
    ax1.plot(temp_time,temp_amb_laser,'b',alpha=0.7,label='temp amb laser')
    ax1.plot(temp_time,temp_amb_edfa,'g',alpha=0.7,label='temp amb edfa')
    ax1.plot(temp_time,temp_amb_compu,'k',alpha=0.7,label='temp amb compu')    
    ax1.set_ylim([20, 32])
    ax1.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    ax1.set_xticks(std_time_t)
    ax1.set_xticklabels(std_time_str)
    ax1.legend(loc='upper right')
    ax1.set_title('Monitoreo de temperatura')
    ax1.set_ylabel(u'Temperatura [°C]')
    ax1.set_xlabel('Tiempo')

    #####################
    y_hist_laser,x_hist_laser = np.histogram(matriz_mon_laser/norm_laser_i,bins=bins_hist,range=(0.7,1.3),normed=True)
    x_hist_laser = x_hist_laser[0:len(x_hist_laser)-1]         
    y_hist_laser_acc = (y_hist_laser_acc*j + y_hist_laser)/(j+1)
    
    ax2.cla()
    ax2.plot(x_hist_laser,y_hist_laser,'b',alpha = 0.5,label='actual')
    ax2.plot(x_hist_laser,y_hist_laser_acc,'r',alpha = 0.5,label='acumulado')
    ax2.set_title(u'Histograma de energía láser')
    ax2.set_xlabel(u'Energía normalizada')
    ax2.legend(loc='upper right')
    ax2.set_ylim([0,100])
    

    y_hist_edfa,x_hist_edfa = np.histogram(matriz_mon_edfa/norm_edfa_i,bins=bins_hist,range=(0.7,1.3),normed=True)
    x_hist_edfa = x_hist_edfa[0:len(x_hist_edfa)-1]         
    y_hist_edfa_acc = (y_hist_edfa_acc*j + y_hist_edfa)/(j+1)

    ax3.cla()
    ax3.plot(x_hist_edfa,y_hist_edfa,'b',alpha = 0.5,label='actual')
    ax3.plot(x_hist_edfa,y_hist_edfa_acc,'r',alpha = 0.5,label='acumulado')
    ax3.set_title(u'Histograma de energía EDFA')
    ax3.set_xlabel(u'Energía normalizada')
    ax3.legend(loc='upper right')
    ax3.set_ylim([0,100])
    
    #########################################
    t_set_bloque = matriz_temp[1][ind_i:ind_f]
    t_act_bloque = matriz_temp[2][ind_i:ind_f]
    c_act_bloque = matriz_temp[3][ind_i:ind_f]

    t_set_laser = matriz_temp[4][ind_i:ind_f]
    t_act_laser = matriz_temp[5][ind_i:ind_f]
    c_act_laser = matriz_temp[6][ind_i:ind_f]
    
    t_t = tiempo_temp[ind_i:ind_f]
    
    t_set_bloque = np.convolve(t_set_bloque,np.ones(bins_conv)/bins_conv,mode='valid')
    t_act_bloque = np.convolve(t_act_bloque,np.ones(bins_conv)/bins_conv,mode='valid')
    c_act_bloque = np.convolve(c_act_bloque,np.ones(bins_conv)/bins_conv,mode='valid')
    
    t_set_laser = np.convolve(t_set_laser,np.ones(bins_conv)/bins_conv,mode='valid')
    t_act_laser = np.convolve(t_act_laser,np.ones(bins_conv)/bins_conv,mode='valid')
    c_act_laser = np.convolve(c_act_laser,np.ones(bins_conv)/bins_conv,mode='valid')    
      
    t_t = t_t[0:len(c_act_laser)]       
    t_tec.extend(t_t)
    
    diff_bloque = []
    diff_laser = []
    diff_cor_bloque = []
    diff_cor_laser = []  
    
    if (j==0):
        norm_cor_bloque = np.mean(np.asarray(c_act_bloque))
        norm_cor_laser = np.mean(np.asarray(c_act_laser))
    
    for i in range(len(t_set_bloque)):
        diff_bloque.append(t_set_bloque[i]-t_act_bloque[i])
        diff_laser.append(t_set_laser[i]-t_act_laser[i])
        
        diff_cor_bloque.append(c_act_bloque[i]-norm_cor_bloque)
        diff_cor_laser.append(c_act_laser[i]-norm_cor_laser)
    
       
    
    diff_bloque_acc.extend(diff_bloque)
    diff_laser_acc.extend(diff_laser)
    
    diff_cor_bloque_acc.extend(diff_cor_bloque)
    diff_cor_laser_acc.extend(diff_cor_laser)    
    
    delta_t = t_tec[len(t_tec)-1] - t_tec[0]
    delta_t = delta_t.total_seconds()   

    if (delta_t >= filas_seg):
        t_tec = t_tec[len(t_t):len(t_tec)]
        diff_bloque_acc = diff_bloque_acc[len(diff_bloque):len(diff_bloque_acc)]
        diff_laser_acc = diff_laser_acc[len(diff_laser):len(diff_laser_acc)]

        diff_cor_bloque_acc = diff_cor_bloque_acc[len(diff_cor_bloque):len(diff_cor_bloque_acc)]
        diff_cor_laser_acc = diff_cor_laser_acc[len(diff_cor_laser):len(diff_cor_laser_acc)]
    
    ax4.cla()
    ax44.cla()
    ax4.plot(t_tec,diff_bloque_acc,'b',alpha = 0.5,label='bloque')
    ax4.plot(t_tec,diff_laser_acc,'r',alpha = 0.5,label='laser')

    ax44.plot(t_tec,diff_cor_bloque_acc,'g',alpha = 0.5,label='bloque')
    ax44.plot(t_tec,diff_cor_laser_acc,'y',alpha = 0.5,label='laser')


    ax4.set_ylim([-0.1,0.1])
    ax4.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    ax4.set_xticks(std_time_t)
    ax4.set_xticklabels(std_time_str)
    
    ax4.set_title(u'Control TEC')
    ax4.set_ylabel(u'Diff. Temperatura [°C]')
    ax4.set_xlabel(u'Tiempo')
    ax4.legend(loc='upper left')   
    
    ax44.set_ylim([-0.30,0.02])
    ax44.set_ylabel(u'Diff. Corriente [A]')
    ax44.legend(loc='upper right')  
    
    ############################################
    
    
    ind_i = ind_f
    
    #print tiempo_ini_j, tiempo_fin_j

    #matriz_std, tiempo_filas_std, pos_bin, = carga_matriz_std(parametros_std)
    
    
#    header, vector = data_read(header_path, path, vec_fils, vec_cols)  # lee los datos y los recupera en el vector 2d
#    
#    f = j % (filas / step)  # resto de iteración / iteraciones en un waterfall completo
#    
#    data = root.data
#    if (f == 0):
#        data = np.zeros((filas, columnas), dtype=eval(header['PythonNpDataType']))




print frames_tot

root = Tk.Tk()

fig = Figure(figsize=(14, 7), dpi=250)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0, row=1, columnspan=10)  

a = np.zeros(filas)
# Suplot del Waterfall
ax = fig.add_axes([.07, .57, .38, .37])
ax0 = ax.twinx()
ax.set_title(u'Monitoreo de Laser-EDFA')
ax.set_ylabel(u'Ruido Normalizado')
ax0.set_ylabel(u'Energía Normalizada')

ax1 = fig.add_axes([.07, .07, .38, .37])
ax11 = ax1.twinx()
ax1.set_title('Monitoreo de temperatura')
ax1.set_ylabel(u'Temperatura [°C]')


ax2 = fig.add_axes([.56, .57, .18, .37])
ax2.set_title(u'Histograma de energía LASER')
ax2.set_ylabel(u'Ruido Normalizado')
ax2.set_xlabel(u'Energía Normalizada')

ax3 = fig.add_axes([.78, .57, .18, .37])
ax3.set_title(u'Histograma de energía EDFA')
ax3.set_ylabel(u'Ruido Normalizado')
ax3.set_xlabel(u'Energía Normalizada')


ax4 = fig.add_axes([.56, .07, .38, .37])
ax44 = ax4.twinx()
ax4.set_title(u'Control TEC')
ax4.set_ylabel(u'Diff. Temperatura [°C]')
ax4.set_xlabel(u'Tiempo')


ani = animation.FuncAnimation(fig, updatefig, interval=0.2, blit=False, frames=frames_tot, repeat=False)
ani.save(output_movie, writer=writer, dpi=250)
plt.show()

