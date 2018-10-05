# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 22:23:45 2017

@author: Marco
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure






def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
                


def header_read(nombre_archivo):
    fid = open(nombre_archivo, "r")
    
    line =  []
    header_size = 0
    header_campo = []
    header_valor = []
    
    
    while (1):
        line = fid.readline()
        if (line=='Fin header \n'):
            break
        
        header_size += len(line.encode('utf-8'))
        valor = find_between( line, "'", "'" )
        pos = line.find(':')
        campo = line[0:pos:]
        
        if not valor:
            valor = find_between( line, "[", "]" )
            valor = float(valor)
        
        header_campo.append(campo)
        header_valor.append(valor)
        
        exec(campo + " = valor") #paso los campos a variables
    fid.close()
    header_size += len(line.encode('utf-8'))
    
    file_size = os.path.getsize(nombre_archivo)
    
    header_campo.append('Header_size')   
    header_valor.append(header_size)  
    header_campo.append('File_size')   
    header_valor.append(file_size)     
    
    data_size = file_size-header_size
    Fils = data_size/BytesPerDatum/Cols
    
    header_campo.append('Fils')
    header_valor.append(Fils) 
    
    return header_campo, header_valor, header_size
    


def data_read(nombre_archivo):
    
    header_campo, header_valor, header_size = header_read(nombre_archivo)
    
    for i in range(0,len(header_campo)):
        valor = header_valor[i]
        campo = header_campo[i]
        exec(campo + " = valor")
        
    #print Fils, Cols, PythonNpDataType
    
    fid = open(nombre_archivo,'rb')
    fid.seek(header_size, 0)
    exec("D1 = np.fromfile(fid, dtype="+PythonNpDataType+",count=int(Fils*Cols))")
    fid.close
    
    return header_campo, header_valor, D1     

  
nombre_archivo = "17_19_07_08_51_48.std"     
header_campo, header_valor, D1 = data_read(nombre_archivo)
for i in range(0,len(header_campo)):
    valor = header_valor[i]
    campo = header_campo[i]
    exec(campo + " = valor")



data1 = np.reshape(D1,(np.int(Fils),np.int(Cols)))
plt.imshow(data1, cmap=plt.get_cmap('jet'),aspect='auto',interpolation='none')
plt.colorbar()









