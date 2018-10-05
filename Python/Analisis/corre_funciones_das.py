######################################
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 09:32:54 2017

@author: Marco
"""

#################
# procesa_std_fft: esta función lee el dato crudo y procesa para obtener la STD y la FFT.

from funciones_das import procesa_std_fft
from funciones4 import header_read
from funciones4 import data_read
import numpy as np


parametros = {}
parametros['time_str'] = '18_06_04_20_17_12'
parametros['c'] = 299792458.
parametros['n'] = 1.493986163
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['offset_m'] = 336.1150
parametros['FrecLaser'] = 10000
parametros['zoom_i_m'] = 3000
parametros['zoom_f_m'] = 4000
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.2
parametros['punzados_m'] = np.array([])  # np.array([3800,3795,3689,3665,3580,3565,3499,3478,3462,3425,3411])
parametros['colores_m'] = []  # ['r','r','g','g','k','k','r','r','r','c','c']
parametros['titulo_str'] = 'Retro a 4 m de la traza'
parametros['tiempo_ini'] = ''  # '2017-11-30 11:12:30'
parametros['tiempo_fin'] = ''  # '2017-11-30 11:13:30'
parametros['window_time_data'] = 20
parametros['window_bin_data'] = 1
parametros['window_bin'] = 5
parametros['window_bin_mean'] = 1
parametros['std_step_sec'] = 1
parametros['butter_filter'] = 'no'
parametros['butter_lp_frec'] = 1000
parametros['butter_hp_frec'] = 5
parametros['butter_order'] = 5
parametros['fft_step_sec'] = 10
parametros['c_axis_min_fft'] = 0
parametros['c_axis_max_fft'] = 10000
parametros['titulo_str_fft'] = 'FFT de retro a 4 m de la traza'
parametros['guarda_figuras'] = 'si'
parametros['carpeta_figuras'] = 'Figuras'
parametros['num_figura'] = 1

std, data_fft_tot, pos_bin_std, tiempo_filas_std, frq, pos_bin_fft, = procesa_std_fft(parametros)


##########################
# carga_std: carga los datos de la std en una matriz[filas=tiempo, col=bines].
# Verificar FrecLaser, tiempo_ini y tiempo_fin
from funciones_das import carga_std
from funciones4 import header_read
from funciones4 import data_read
import numpy as np
import os

parametros = {}
parametros['time_str'] = '17_22_11_12_04_36'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros['c'] = 299792458.
parametros['n'] = 1.46879964
parametros['offset_m'] = 0
parametros['FrecLaser'] = 5000
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['vector_offset'] = np.zeros(int(header['Cols']))
parametros['vector_norm'] = np.ones(int(header['Cols']))
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.2
parametros['zoom_i_m'] = 0
parametros['zoom_f_m'] = 13000
parametros['marcadores_m'] = np.array([1000, 2000, 3000])
parametros['marcadores_texto'] = ['V1', 'V2', 'V3']
parametros['marcadores_waterfall'] = 'no'
parametros['marcadores_color'] = ['r', 'r', 'r']
parametros['titulo_str'] = 'Oleoducto Restinga'
parametros['tiempo_ini'] = '2017-11-22 12:40:00'
parametros['tiempo_fin'] = '2017-11-22 12:50:00'
parametros['guarda_figuras'] = 'si'
parametros['carpeta_figuras'] = 'Figuras'
parametros['num_figura'] = 1

matriz, tiempo_filas_std, pos_bin, = carga_std(parametros)


###########################
# peli_std: genera una pelicula del waterfall con los datos de la STD.
# Verificar FrecLaser.

from funciones_das import peli_std
from funciones4 import header_read
from funciones4 import data_read
import numpy as np
import os

# Puesta en profundiad 
bin_i = 335.
bin_f = 4251.
z_pozo = 3962.34
delta_x = z_pozo/(bin_f-bin_i)
delta_t = 1/100e6
c = 299792458.
c_f = 2*delta_x/delta_t    
n = c/c_f    
offset_x = bin_i*delta_x


parametros = {}
parametros['time_str'] = '18_06_04_20_17_12'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['carpeta'] = ''
parametros['carpeta_std'] = 'STD'
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2_full_pozo.mp4')
parametros['c'] = 299792458.
parametros['n'] = 1.48143176194
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['offset_m'] = -334.
parametros['FrecLaser'] = 10000
parametros['FilasPeli'] = 5000
parametros['StepPeli'] = 200
parametros['vector_offset'] = np.zeros(int(header['Cols']))
parametros['vector_norm'] = np.ones(int(header['Cols']))
parametros['titulo_str'] = '%02d' % (1)
parametros['texto1'] = 'EFO189'
parametros['texto2'] = ''
parametros['tiempo_ini'] = '2018-04-06 20:20:00'
parametros['tiempo_fin'] = '2018-04-10 13:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.2
parametros['zoom_i_m'] = 0000
parametros['zoom_f_m'] = 4000
parametros['marcadores_m'] = np.array([3347, 3367, 3389, 3413,3415, 3552,3572, 3612,3631, 3663,3666, 3687,3696 ,3716, 3827,3831, 3873,3878])
parametros['marcadores_texto'] = ['E8', ' ', ' ', 'E7',' ', 'E6',' ', 'E5',' ', 'E4',' ', 'E3',' ',' ', 'E2',' ', 'E1',' ']
parametros['marcadores_waterfall'] = 'no'
parametros['marcadores_color'] = ['r', 'r', 'r', 'g','g', 'k','k', 'y','y', 'b','b', 'r', 'r','r', 'g','g', 'k','k']
parametros['guarda_figuras'] = 'no'
parametros['carpeta_figuras'] = 'Figuras'

peli_std(parametros)


############
parametros['time_str'] = '18_13_04_09_21_03'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-13 09:25:00'
parametros['tiempo_fin'] = '2018-04-16 16:30:00'
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2_full_pozo.mp4')
parametros['zoom_i_m'] = 0000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_13_04_09_21_03'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-13 09:25:00'
parametros['tiempo_fin'] = '2018-04-16 16:30:00'
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2.mp4')
parametros['zoom_i_m'] = 3000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_19_04_00_13_36'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-22 12:00:00'
parametros['tiempo_fin'] = '2018-04-23 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2.mp4')
parametros['zoom_i_m'] = 0000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_19_04_00_13_36'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-22 09:00:00'
parametros['tiempo_fin'] = '2018-04-23 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_19_04_00_13_36'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-22 12:00:00'
parametros['tiempo_fin'] = '2018-04-23 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2a.mp4')
parametros['zoom_i_m'] = 0000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_19_04_00_13_36'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-22 12:00:00'
parametros['tiempo_fin'] = '2018-04-23 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3a.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_11_04_17_34_04'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-11 17:35:00'
parametros['tiempo_fin'] = '2018-04-12 11:30:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2a.mp4')
parametros['zoom_i_m'] = 0000
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_11_04_17_34_04'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-11 17:35:00'
parametros['tiempo_fin'] = '2018-04-12 11:30:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3a.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)



############
parametros['time_str'] = '18_28_03_16_39_34'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-03-28 17:00:00'
parametros['tiempo_fin'] = '2018-04-02 07:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2a.mp4')
parametros['zoom_i_m'] = -300
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_28_03_16_39_34'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-03-28 17:00:00'
parametros['tiempo_fin'] = '2018-04-02 07:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3a.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)



############
parametros['time_str'] = '18_11_04_17_34_04'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-11 17:40:00'
parametros['tiempo_fin'] = '2018-04-12 11:30:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2a.mp4')
parametros['zoom_i_m'] = -300
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_11_04_17_34_04'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-11 17:40:00'
parametros['tiempo_fin'] = '2018-04-12 11:30:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3a.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)



############
parametros['time_str'] = '18_16_04_16_35_43'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-16 16:40:00'
parametros['tiempo_fin'] = '2018-04-18 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli2a.mp4')
parametros['zoom_i_m'] = -300
parametros['zoom_f_m'] = 4000

peli_std(parametros)


############
parametros['time_str'] = '18_16_04_16_35_43'
nombre_header = os.path.join(parametros['time_str'], 'STD', 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], 'STD', '000000.std')  # De no tener el 000000.std poner el archivo .std inicial que se tenga.
header = header_read(nombre_header, nombre_archivo)
parametros['tiempo_ini'] = '2018-04-16 16:40:00'
parametros['tiempo_fin'] = '2018-04-18 09:00:00'
parametros['c_axis_min'] = 0
parametros['c_axis_max'] = 0.15
parametros['FilasPeli'] = 2000
parametros['StepPeli'] = 100
parametros['output_movie'] = os.path.join(parametros['carpeta'], parametros['time_str'], 'STD', 'peli3a.mp4')
parametros['zoom_i_m'] = 2000
parametros['zoom_f_m'] = 4000

peli_std(parametros)














###########################
# carta_matriz_std: carga la matriz STD (filas=tiempo, col=bines)
# Verificar FrecLaser.

from funciones_das import carga_matriz_std
from funciones_das import carga_matriz_avg
from funciones4 import header_read
from funciones4 import data_read
import numpy as np
import os



# Puesta en profundiad 
bin_i = 335.
bin_f = 4251.
z_pozo = 3962.34
delta_x = z_pozo/(bin_f-bin_i)
delta_t = 1./100e6
c = 299792458.
c_f = 2*delta_x/delta_t    
n = c/c_f    
offset_x = bin_i*delta_x


bin_f*delta_x-offset_x


parametros = {}
parametros['time_str'] = '18_06_04_20_17_12'
parametros['carpeta_std'] = 'STD'
nombre_header = os.path.join(parametros['time_str'], parametros['carpeta_std'], 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], parametros['carpeta_std'], '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros['c'] = 299792458.
parametros['n'] = 1.51670026
parametros['offset_m'] = -331
parametros['FrecLaser'] = 10000
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['zoom_i_m'] = -300
parametros['zoom_f_m'] = 4200
parametros['tiempo_ini'] = '2018-04-06 20:20:00'
parametros['tiempo_fin'] = '2018-04-07 00:15:00'
matriz, tiempo_filas_std, pos_bin, = carga_matriz_std(parametros)

parametros_avg = {}
parametros_avg['time_str'] = '18_06_04_20_17_12'
parametros_avg['carpeta_std'] = 'AVG'
nombre_header = os.path.join(parametros['time_str'], parametros_avg['carpeta_std'], 'avg.hdr')
nombre_archivo = os.path.join(parametros['time_str'], parametros_avg['carpeta_std'], '000000.avg')
header = header_read(nombre_header, nombre_archivo)
parametros_avg['c'] = 299792458.
parametros_avg['n'] = 1.51670026
parametros_avg['offset_m'] = -331
parametros_avg['FrecLaser'] = 10000
parametros_avg['c_f'] = parametros['c'] / parametros['n']
parametros_avg['zoom_i_m'] = -300
parametros_avg['zoom_f_m'] = 4200
parametros_avg['tiempo_ini'] = '2018-04-06 20:20:00'
parametros_avg['tiempo_fin'] = '2018-04-07 00:15:00'
avg, tiempo_filas_std1, pos_bin1, = carga_matriz_avg(parametros_avg)


matriz = matriz/avg



import matplotlib.pyplot as plt

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.08, .1, .8, .8])
ax.plot(pos_bin1,np.mean(matriz,axis = 0))
#im = ax.imshow(matriz, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
#im.set_clim([0, 0.2])
#fig.colorbar(im)
plt.show()


#########################
parametros = {}
parametros['time_str'] = '18_09_04_16_14_46'
parametros['carpeta_std'] = 'STD_NORM'
nombre_header = os.path.join(parametros['time_str'], parametros['carpeta_std'], 'std.hdr')
nombre_archivo = os.path.join(parametros['time_str'], parametros['carpeta_std'], '000000.std')
header = header_read(nombre_header, nombre_archivo)
parametros['c'] = 299792458.
parametros['n'] = 1.46879964
parametros['offset_m'] = 0
parametros['FrecLaser'] = 2000
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['zoom_i_m'] = 0
parametros['zoom_f_m'] = 5600
parametros['tiempo_ini'] = '2018-04-09 16:15:00'
parametros['tiempo_fin'] = '2018-04-09 18:15:00'
matriz1, tiempo_filas_std1, pos_bin1, = carga_matriz_std(parametros)






#########################
from funciones_das import carga_matriz_raw
from funciones4 import header_read
from funciones4 import data_read
import os



parametros = {}
parametros['time_str'] = '18_08_08_22_50_36'
parametros['carpeta_raw'] = 'RAW_CH0'
nombre_header = os.path.join(parametros['time_str'], parametros['carpeta_raw'], 'ch0.hdr')
nombre_archivo = os.path.join(parametros['time_str'], parametros['carpeta_raw'], '000000.bin')
header = header_read(nombre_header, nombre_archivo)
parametros['c'] = 299792458.
parametros['n'] = 1.46879964
parametros['offset_m'] = 0
parametros['FrecLaser'] = 10000
parametros['c_f'] = parametros['c'] / parametros['n']
parametros['zoom_i_m'] = 0
parametros['zoom_f_m'] = 5
parametros['tiempo_ini'] = '2018-08-08 22:53:55'
parametros['tiempo_fin'] = '2018-08-08 22:55:22'
parametros['header_file'] = 'ch0.hdr'

matriz1, tiempo_filas_raw, pos_bin1, = carga_matriz_raw(parametros)





import matplotlib.pyplot as plt

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.08, .1, .8, .8])
im = ax.imshow(matriz, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
im.set_clim([0, 0.2])
fig.colorbar(im)
plt.show()

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.08, .1, .8, .8])
im = ax.imshow(matriz1, cmap=plt.get_cmap('jet'), aspect='auto', interpolation='none')
im.set_clim([0, 0.2])
fig.colorbar(im)
plt.show()


ax.set_xticks([0,10,300])

###########################
# carta_matriz_std: carga la matriz STD (filas=tiempo, col=bines)
# Verificar FrecLaser.

from funciones_das import carga_matriz_monitoreo
from funciones4 import header_read
from funciones4 import data_read
import numpy as np


parametros = {}
parametros['time_str'] = '18_07_03_17_25_55'
parametros['sub_dir'] = 'MON_LASER'
parametros['FrecLaser'] = 5000
parametros['tiempo_ini'] = '2018-03-07 17:25:55'
parametros['tiempo_fin'] = '2018-03-07 17:35:55'

matriz, tiempo_filas_mon, = carga_matriz_monitoreo(parametros)



###############################################
#  
#

from funciones_das import carga_datos_temperatura

parametros = {}
parametros['file_name'] = '2018_03_07_17_02_43_val.txt'
parametros['tiempo_ini'] = '2018-03-07 17:25:55'
parametros['tiempo_fin'] = '2018-03-07 17:30:55'

matriz, vector_tiempo = carga_datos_temperatura(parametros)


delta_t = vector_tiempo[len(vector_tiempo)-1] - vector_tiempo[0]
delta_t = delta_t.total_seconds()           

matriz[0][0]
matriz[0][len(matriz[0])-1]

###################################################




###############################################
#  
#

from funciones_das import carga_datos_temperatura2

parametros = {}
parametros['time_str'] = '18_20_03_11_22_16'
parametros['tiempo_ini'] = '2018-03-20 20:22:55'
parametros['tiempo_fin'] = '2018-03-20 20:25:10'

matriz, vector_tiempo = carga_datos_temperatura2(parametros)



time_str = '18_20_03_11_22_16'
dt={'names': ('fecha','temp_set_bloque', 'temp_act_bloque', 'corr_bloque', 'temp_set_laser', 'temp_act_laser', 'corr_laser', 'temp1', 'temp2', 'temp3' ),'formats': ('S25','f4','f4','f4','f4','f4','f4','f4','f4','f4')}
path= os.path.join(time_str, 'MONITOREO','000000.val')
data = np.loadtxt(path,delimiter=',', dtype=dt, unpack=True,skiprows=1)              
tiempo_i = datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S.%f')

sorted(os.listdir(os.path.join(parametros['time_str'], 'MONITOREO')), reverse=False)

len(os.listdir(os.path.join(parametros['time_str'], 'MONITOREO')))


delta_t = vector_tiempo[len(vector_tiempo)-1] - vector_tiempo[0]
delta_t = delta_t.total_seconds()           

matriz[0][0]
matriz[0][len(matriz[0])-1]

###################################################

from funciones_das import carga_datos_temperatura3

parametros = {}
parametros['time_str'] = '18_08_08_22_50_36'
parametros['tiempo_ini'] = '2018-08-08 22:55:54'
parametros['tiempo_fin'] = '2018-08-09 02:56:54'
parametros['dt'] = {'names': ('fecha','control_ext', 'frecuencia_laser_hz', 'ancho_de_pulso_ns', 'tec_laser_onoff', 'temp_act_laser_c', 'temp_set_laser_c', 'temp_set_laser1_c', 'tec_bloque_onoff', 'temp_act_bloque_c','temp_set_bloque_c','temp_set_bloque1_c','temp_seguidor_bloque_c','modo_seguidor_bloque','tension_laser_act_mv','tension_laser_set_mv','temp_amb1_c','corriente_tec_laser_ma','corriente_tec_bloque_ma' ),'formats': ('S25','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4')}
parametros['carpeta_monitoreo'] = 'MONITOREO'

matriz, vector_tiempo = carga_datos_temperatura3(parametros)