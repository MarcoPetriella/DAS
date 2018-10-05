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
FrecLaser = 5000
tiempo_ini = '2018-03-07 17:58:00'
tiempo_fin = '2018-03-08 09:00:00'
c = 299792458.
n = 1.46879964
c_f = c/n
zoom_i_m = 6000
zoom_f_m = 8000
step_seg = 100 #segundos
filas_seg = 3600 #segundos
offset_m = 0

output_movie = os.path.join(time_str, 'STD', 'peli_monitoreo.mp4')

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

zoom_i = int((zoom_i_m - offset_m) / delta_x)
zoom_f = int((zoom_f_m - offset_m) / delta_x)
                             
frames_tot = int((((fin_file - ini_file + 1) * filas_0 - (ini_fila) - (filas_0 - fin_fila)) / step))

vec_cols = np.array([0, header['Cols'] - 1], dtype=np.uint64)
cols_to_read = vec_cols[1] - vec_cols[0] + 1

parametros_std = {}
parametros_std['time_str'] = time_str
parametros_std['c'] = c
parametros_std['n'] = n
parametros_std['offset_m'] = offset_m
parametros_std['FrecLaser'] = FrecLaser
parametros_std['c_f'] = parametros_std['c'] / parametros_std['n']
parametros_std['zoom_i_m'] = zoom_i_m
parametros_std['zoom_f_m'] = zoom_f_m              


parametros_mon_laser = {}
parametros_mon_laser['time_str'] = time_str
parametros_mon_laser['sub_dir'] = 'MON_LASER'
parametros_mon_laser['FrecLaser'] = 5000

parametros_mon_edfa = {}
parametros_mon_edfa['time_str'] = time_str
parametros_mon_edfa['sub_dir'] = 'MON_EDFA'
parametros_mon_edfa['FrecLaser'] = 5000
              
parametros_temp = {}
parametros_temp['file_name'] = '2018_03_07_17_55_59_val.txt'
                  
tiempo_fin_j = tiempo_ini
     

std_mean = []     
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
       
def updatefig(j):
    global tiempo_fin_j, std_mean, std_time, vec_ruido_mon_laser, vec_ruido_mon_edfa, mon_time, vec_mon_laser, vec_mon_edfa, temp_time, temp_amb_laser, temp_amb_edfa, temp_amb_compu
    print float(j/frames_tot)*100.
    #print 'hola'
    
    tiempo_ini_j = tiempo_fin_j
    tiempo_fin_j_d = datetime.datetime.strptime(tiempo_ini_j, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=step_seg)
    tiempo_fin_j = tiempo_fin_j_d.strftime("%Y-%m-%d %H:%M:%S") 

    parametros_std['tiempo_ini'] = tiempo_ini_j
    parametros_std['tiempo_fin'] = tiempo_fin_j

    parametros_mon_laser['tiempo_ini'] = tiempo_ini_j
    parametros_mon_laser['tiempo_fin'] = tiempo_fin_j
                  
    parametros_mon_edfa['tiempo_ini'] = tiempo_ini_j
    parametros_mon_edfa['tiempo_fin'] = tiempo_fin_j

    parametros_temp['tiempo_ini'] = tiempo_ini_j
    parametros_temp['tiempo_fin'] = tiempo_fin_j
                   
                
    matriz_std, tiempo_filas_std, pos_bin_std, = carga_matriz_std(parametros_std)             
    matriz_mon_laser, tiempo_filas_mon_laser = carga_matriz_monitoreo(parametros_mon_laser)      
    matriz_mon_edfa, tiempo_filas_mon_edfa = carga_matriz_monitoreo(parametros_mon_edfa)  
    matriz_temp,tiempo_temp = carga_datos_temperatura(parametros_temp)
        
    x_std = np.mean(matriz_std,axis = 1)   
    std_mean = np.append(std_mean,x_std)   
    std_time.extend(tiempo_filas_std)     
    delta_t = std_time[len(std_time)-1] - std_time[0]
    delta_t = delta_t.total_seconds()
    
    if (delta_t >= filas_seg):
        std_time = std_time[len(tiempo_filas_std):len(std_time)]
        std_mean = std_mean[len(tiempo_filas_std):len(std_mean)]


    vec_ruido_mon_laser = np.append(vec_ruido_mon_laser,np.std(matriz_mon_laser,axis=1)/np.mean(matriz_mon_laser,axis=1))
    vec_ruido_mon_edfa = np.append(vec_ruido_mon_edfa,np.std(matriz_mon_edfa,axis=1)/np.mean(matriz_mon_edfa,axis=1))
    vec_mon_laser = np.append(vec_mon_laser,np.mean(matriz_mon_laser,axis=1))
    vec_mon_edfa = np.append(vec_mon_edfa,np.mean(matriz_mon_edfa,axis=1))

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
    ax.plot(std_time,std_mean,'r',alpha=0.5,label='std waterfall')
    ax.plot(mon_time,vec_ruido_mon_laser,'b',alpha=0.5,label='std laser')
    ax.plot(mon_time,vec_ruido_mon_edfa,'g',alpha=0.5,label='std edfa')

    ax0.plot(mon_time,vec_mon_laser,'--b',alpha=0.5,label='medio laser')
    ax0.plot(mon_time,vec_mon_edfa,'--g',alpha=0.5,label='medio edfa')
    
    ax.set_ylim([0,0.1])
    ax0.set_ylim([5000,20000])
    ax.legend(loc='upper right')
    ax0.legend(loc='upper left')
    
    ax.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    ax0.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    
    #########################################
    temp_amb_laser.extend(matriz_temp[8]) 
    temp_amb_edfa.extend(matriz_temp[7]) 
    temp_amb_compu.extend(matriz_temp[9]) 


    temp_time.extend(tiempo_temp)  
    delta_t = temp_time[len(temp_time)-1] - temp_time[0]
    delta_t = delta_t.total_seconds()   

    if (delta_t >= filas_seg):
        temp_time = temp_time[len(tiempo_temp):len(temp_time)]
        temp_amb_laser = temp_amb_laser[len(matriz_temp[8]):len(temp_amb_laser)]
        temp_amb_edfa = temp_amb_edfa[len(matriz_temp[7]):len(temp_amb_edfa)]
        temp_amb_compu = temp_amb_compu[len(matriz_temp[9]):len(temp_amb_compu)]
        
        


    ax1.cla()
    ax1.plot(temp_time,temp_amb_laser,'b',alpha=0.5,label='temp amb laser')
    ax1.plot(temp_time,temp_amb_edfa,'g',alpha=0.5,label='temp amb edfa')
    ax1.plot(temp_time,temp_amb_compu,'k',alpha=0.5,label='temp amb compu')    
    ax1.set_ylim([20, 30])
    ax1.set_xlim([mon_time[0],mon_time[len(mon_time)-1]])
    ax1.legend(loc='upper right')

    
    
    

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
ax = fig.add_axes([.07, .6, .4, .35])
ax0 = ax.twinx()

ax1 = fig.add_axes([.07, .07, .4, .35])
ax11 = ax1.twinx()



ani = animation.FuncAnimation(fig, updatefig, interval=0.2, blit=False, frames=frames_tot, repeat=False)
ani.save(output_movie, writer=writer, dpi=250)
plt.show()
Tk.mainloop()

