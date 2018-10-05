/// Ch0: señal APD
/// Ch1: señal monitoreo. Laser+EDFA equipo DAS OLEO 1


/// (2.8.2) Cambios respecto a version 2.8.1:
/// En Thread STD: agrego la posibilidad de hacer la STD Normalizada respecto al moving average del perfil (agrego parametro de entrada window_bin_mean)
/// En Thread FFT: si se adquiere un solo canal la FFT no explota (estaba hecha para cuando se adquirian dos canales). Se explicita nCh
/// En Thread Raw_Data: Se imprime la velocidad de escritura para monitoreo
/// En Thread Monitoreo: Se explicita el nCh en la cuenta (medio al dope porqe si nCh = 1 el thread no se ejecuta)
/// En Main: Si nCh = 1, el thread monitoreo no se ejecuta.
/// Cambio funcion moving1avg: caso window = 1
/// La apertura de los datos en python se realiza con las funciones especificas puestas en funciones2.py

/// (2.9.2) Cambios respecto a version 2.8.2:
/// Se puede grabar independientemente los dos canales Ch0 y Ch1

/// (2.9.4) Cambios respecto a version 2.9.3:
/// El copiado del buffer se hace con la funcion memcpy_s que avisa cuando hay error en el copiado.

/// (2.9.5) Cambios respecto a version 2.9.4:
/// Divide la FFT por nShotsChk. El pipe de visualizacion llama fft_test_1 en vez de fft_test. fft_test_1 es gui.

/// (2.9.6) Cambios respecto a version 2.9.5:
/// Escribe los archivos de salida en archivos de menor tamano para evitar perder los datos en caso de corte imprevisto de energia durante la adquisicion.
/// Se agrega parametro de guardado ChunksSave en config.ini: cantidad de chunks que se guardan por archivo.

/// (2.9.7) Cambios respecto a version 2.9.6:
/// Escribe los archivos de salida partidos en tamanos chicos y los pone en distintas carpetas segun el tipo de dato. Por cada carpeta (o tipo de dato)
/// escribe un header que contiene la informacion necesaria para abrir los archivos.
/// La apertura de los datos en python se realiza con las funciones especificas puestas en funciones3.py (las tengo que escribir todavia)
/// Carpetas:
/// -RAW_CH0: dato crudo del canal 0
/// -RAW_CH1: dato crudo del canal 1
/// -RAW_CH: dato crudo de los canales 0 y 1 en un mismo archivo
/// -STD: dato procesado
/// -MON_LASER: monitoreo de la estabilidad del laser
/// -MON_EDFA: monitoreo de la estabilidad del pulso amplificado por el edfa
/// -TIME: tiempo de guardado de cada chunk en el HD
/// Agrego el parámetro Delay al header (me lo habia olvidado)
///
/// (3.0) Cambios respecto a version 2.9.7:
/// 17/08/2017: Se castea el chkBuffer como long long. En las versiones anteriores se verificaba error cuando el chkBuffer superaba el tamaño de un long (4 bytes). Ahora el chkBuffer puede superar ese valor.
/// 17/08/2017: Se verifica error de la placa cuando el tamaño del buffer de la placa supera los 128MS. NO RESUELTO.
///
/// (3.1) Cambios respecto a version 3.0:
/// 26/08/2017: Se agrega otro parametro a la adquisición nSubChunk para resolver las limitaciones en el tamaño del buffer de la placa (ver ultimo punto de la version anterior). Este parámetro es un numero entero
///             que divide el chunk de nShotsChk en particiones pequeñas de tamaño nShotsChk/nSubChunk. Cada chunk ahora esta formado de nSubChunk pedazos. El semaforo se activa cuando se llena todo un chunk (es decir todos los nSubChunk).
///             Se modifican el callback y la función adquirir, que recibe un nueva variable de entrada (nSubChunk).
///
/// (3.2) Cambios respecto a version 3.1:
/// 27/08/2017: Se agrega la posibilidad de guardar dato crudo en un rango de bines. Para esto se agregan dos nuevos parámetros.
///             - Bins_raw: bins que se escriben de dato crudo
///             - Delay_raw: delay para el dato crudo. El Delay_raw es respecto de la adquisición. Es decir el delay total de la escritura del dato crudo es Delay + Delay_raw
///
/// (4.0) Cambios respecto a version 3.2:
/// 29/09/2017: Rehace la cuenta para calcular la STD de manera mas eficiente, la calcula a medida que recorre el chunk en orden. De esta manera el proceso STD no se atrasa cuando se adquiere gran cantidad de bins
///             Esto se debe cuantificar.


/// std_fft_osc_2.0 (30/07/2018)
/// Permite hacer el filtro de media 2d antes de calcular la STD. Ahora los parametros del filtro son window_time para los shots, y window_bin para los bines. window_bin_std hace un filtro de media al vector std.
/// Este filtro deberia bajar el ruido de la medición.

/// std_fft_osc_bandas_2.1 (10/8/2018)
/// Realiza la STD normalizada por la energía del pulso EDFA.
/// Realiza el calculo de potencia por bandas en el hilo de la FFT. Se agrega un nuevo pipe para la visualizacion de las bandas (fft_bandas_interfaz_1.py).
/// Se agrega pipe para pasar los parametros de las bandas.

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <windows.h>
#include <process.h>
#include <conio.h>
#include <math.h>
#include <memory.h>
#include "WD-dask64.h"
#include "fftw3.h"

// renombra algunos parámetros de la placa para usarlos en las funciones. los de la derecha significan algo para la placa
#define TIMEBASE      WD_IntTimeBase
#define ADTRIGSRC     WD_AI_TRGSRC_ExtD
#define ADTRIGMODE    WD_AI_TRGMOD_DELAY
#define ADTRIGPOL     WD_AI_TrgPositive
#define BUFAUTORESET  1

#define CARDNUM 0
#define CHUNKS 100
#define CONSUMIDORES 5


typedef enum { false, true } bool;

double PCFreq = 0.0;
__int64 CounterStart = 0;

void StartCounter()
{
    LARGE_INTEGER li;
    if(!QueryPerformanceFrequency(&li)){printf("QueryPerformanceFrequency failed!\n");}


    PCFreq = ((double)li.QuadPart)/1000.0;

    QueryPerformanceCounter(&li);
    CounterStart = li.QuadPart;
}
double GetCounter()
{
    LARGE_INTEGER li;
    QueryPerformanceCounter(&li);
    return ((double)li.QuadPart-CounterStart)/PCFreq;


}

// en la estructura callback estamos juntamos todas las variables externas que utiliza la funciòn AI_CallBack
short* chkBuffer;

bool salir=false;
bool salir_raw=false;
bool salir_std=false;
bool salir_monitoreo=false;
bool salir_fft=false;
bool salir_osc=false;

HANDLE pipeSTD;
HANDLE pipeMONITOREO;
HANDLE pmut;

struct {
    int nCh;
    int bins;
    int nShotsChk;
    int nSubChk;
    int cnt_SubChk;
    int chkActual;
    bool bufferActual;
    short* ai_buf;
    short* ai_buf2; // este es un puntero short porque los elementos del buffer de la placa son shorts, cuando lo indexemos se va a mover de a un short en memoria, de forma de ir pasando de elemento a elemento.
    bool disponible[CHUNKS];
    bool ovr;
    //int contadorPozo; // contador: indica en que chunk estamos para este pozo
    //int chunksPorPozo;// cantiad de chunks por Pozo
    //bool pausa; // este indica si esteamos eperando que se ejecute el cambio de pozo
    //HANDLE cambio_pozo; // defini un envento para avisar que se debe cambiar de pozo
    HANDLE semConsumidor[CONSUMIDORES];
}callback;


struct {
    int banda_ai;
    int banda_af;
    int banda_bi;
    int banda_bf;
    int banda_ci;
    int banda_cf;

}bandas;

typedef struct COMMTIMEOUTS {
  DWORD ReadIntervalTimeout;
  DWORD ReadTotalTimeoutMultiplier;
  DWORD ReadTotalTimeoutConstant;
  DWORD WriteTotalTimeoutMultiplier;
  DWORD WriteTotalTimeoutConstant;
} COMMTIMEOUTS_s;


/* se definen como globales los tipos de datos que utilizan los procesos. Los porcesos no admiten ningún tipo de argumento
 porque es un creador de una función, tiene que ser capaz de poder ejecutar culaquier cosa. Lo que se hace es pasarle un puntero a void y en esa dirección se
 cargan todos los parámetros que necesita el proceso. La única alternativa es tener todas las variables del proceso como globales. Una vez definido el tipo
 cuando se lanza el proceso se crea un estructura particular del tipo correspondiente y se le pasa la dirección de memoria al proceso. dentro del proceso
 se accede a las variables*/

typedef struct th_Data{
    int bins;
    int delay;
    int nShotsChk;
    int nCh;
    int qFreq;
    long long nShots;
    bool infinite_daq;

    // Para RAW
    int bins_raw;
    int delay_raw;

    // Para STD
    int window_time;
    int window_bin;
    int window_bin_std;
    int window_bin_mean;

    // Para STD
    int bin_mon_laser_i;
    int bin_mon_laser_f;
    int bin_mon_edfa_i;
    int bin_mon_edfa_f;
    int window_mon_time;

    // Para FFT
    int chunk_fft_salteo;
    int chunk_fft_promedio;

    char* placa;
    char* fname_dir;
    char* name_pozos[10];

    int chunks_save;
    bool normaliza_energia;
    bool rawsave_ch0;
    bool rawsave_ch1;
    bool stdsave;
    bool mon_laser_save;
    bool mon_edfa_save;

    // Para OSC
    int cant_curvas;
    int window_time_osc;

    float cLaser;
    float cEDFA;

}th_Data;


float* moving1avg(float* vector,unsigned int vector_size ,unsigned int window, float* vector_avg, unsigned int vector_avg_size){

    int i;
    int j;
    float sum_i = 0.0;
    if (window > 1){
        for(i=0;i<vector_avg_size;++i){
            if(i==0){
                    for(j=0;j<window;++j){
                     sum_i += vector[j];
                    }
            } else {
            sum_i += vector[i+window-1] - vector[i-1];
            }
            vector_avg[i] = sum_i/window;
        }
    } else {
        for(i=0;i<vector_avg_size;++i){
             vector_avg[i] = vector[i];
        }
    }

}

float* moving1avg_full(float* vector,unsigned int vector_size ,unsigned int window, float* vector_avg){

    int i;
    int j;
    float sum_i = 0.0;
    if (window > 1){
        for(i=0;i<vector_size - window+1;++i){
            if(i==0){
                    for(j=0;j<window;++j){
                     sum_i += vector[j];
                    }
            } else {
            sum_i += vector[i+window-1] - vector[i-1];
            }
            vector_avg[i] = sum_i/window;
        }
        j = 1;
        for (i=vector_size - window+1;i<vector_size;++i){
            sum_i -= vector[i-1];
            vector_avg[i] = sum_i/(window-j);
            j++;
        }

    } else {
        for(i=0;i<vector_size;++i){
             vector_avg[i] = vector[i];
        }
    }

}



void AI_CallBack(){
// sino está en pausa ejecuta normal, está en pausa mientras espera el cambio de pozo
   // printf("entro");
    //if(!callback.pausa){
        short* bufferPlaca;

    // le pasamos la dirección de memoria del primer elemento del buffer donde escribió la placa
        if (callback.bufferActual){
                bufferPlaca=callback.ai_buf;
        }else{
                bufferPlaca=callback.ai_buf2;
        }

        //errno_t err;
        callback.cnt_SubChk++;

        if(!callback.disponible[callback.chkActual/callback.nSubChk] ) {
            callback.ovr=true;
            WD_AI_ContBufferReset (CARDNUM);
            WD_Buffer_Free (CARDNUM, callback.ai_buf);
            WD_Buffer_Free (CARDNUM, callback.ai_buf2);
            WD_Release_Card(CARDNUM);
            //return;
        }
        else{ /// NO OVERRUN char command[100];

            if (callback.cnt_SubChk == callback.nSubChk){
                callback.disponible[callback.chkActual/callback.nSubChk]=false;
            }
//          unsigned long chkIndex=(unsigned long)callback.bins*(callback.nCh)*chunkActual*callback.nShotsChk; ///siempre me desplazo bin*cantidad_de_canales*k , k cuenta el shot actual entre 0  y shots_max (buffer circular)
            memcpy(chkBuffer+(long long)callback.bins*(callback.nCh)*callback.chkActual*callback.nShotsChk/callback.nSubChk,bufferPlaca,(long long)callback.bins*callback.nCh*callback.nShotsChk/callback.nSubChk*sizeof(short)); ///copia 2 canales
//          memmove(chkBuffer+callback.bins*(callback.nCh)*callback.chkActual*callback.nShotsChk,bufferPlaca,callback.bins*callback.nCh*callback.nShotsChk*sizeof(I16)); ///copia 2 canales
//          err = memcpy_s(chkBuffer+callback.bins*(callback.nCh)*callback.chkActual*callback.nShotsChk,callback.bins*callback.nCh*callback.nShotsChk*sizeof(I16),bufferPlaca,callback.bins*callback.nCh*callback.nShotsChk*sizeof(I16)); ///copia 2 canales
//          if (err){
//              printf("Error en memcpy\n");
//          }
        }

        DWORD semCount;
        if (callback.cnt_SubChk == callback.nSubChk){
            ReleaseSemaphore(callback.semConsumidor[0],1,&semCount); ///semaforo para ESCRITURA
            ReleaseSemaphore(callback.semConsumidor[1],1,&semCount); ///semaforo para STD
            ReleaseSemaphore(callback.semConsumidor[2],1,&semCount); ///semaforo para MONITOREO
            ReleaseSemaphore(callback.semConsumidor[3],1,&semCount); ///semaforo para FFT
            ReleaseSemaphore(callback.semConsumidor[4],1,&semCount); ///semaforo para Osciloscopio
            callback.cnt_SubChk = 0;
            printf("Mande un chunk \n");
        }

        //printf("productor pasa un chunk\n");

        callback.chkActual=(callback.chkActual+1)%(CHUNKS*callback.nSubChk);
        callback.bufferActual=!callback.bufferActual;



//        callback.contadorPozo++;
//        printf("perfil # %d",callback.contadorPozo);
//        if (callback.contadorPozo==callback.chunksPorPozo){
//            callback.contadorPozo=0;
//            printf("voy a setear el evento\n");
//            SetEvent(callback.cambio_pozo); //sucedió el evento
//            printf("setie el evento\n");
//            callback.pausa=true; //se setea en true para esperar que se consuma el cambio de pozo
//        }


	return;
}



//void* cambio_de_pozo(void* n){
//
//    char* buffer=calloc(10,sizeof(char)); // crea el string y lo inicializa es un malloc inicializado con 0
//    char* cambio="CAMBIAME EL POZO"; // string a enviar a python
//    //lanzar proceso de cambio de pozo en python
//    ConnectNamedPipe(pipePozoCRead,NULL);
//
//    while(true){
//        printf("vivito y coleando\n");
//        WaitForSingleObject(callback.cambio_pozo,INFINITE);
//        printf("por favor Cambia el pozo\n");
//        DWORD leido_pipe,leido_pipe2;
//        WriteFile(pipePozoCWrite,cambio,sizeof(char)*17,&leido_pipe,NULL);
//        ReadFile(pipePozoCRead,buffer,sizeof(char)*10,&leido_pipe2,NULL);
//        if(strcmp(buffer,"CAMBIO OK")==0){// habia un 0
//            callback.pausa=false;
//            memset(buffer,0,10);
//        }else{
//            printf("Falla multiplexer.\n");
//        }
//
//    }
//
//
//}


void adquirir(short nCh, int qFreqAdq, int rangoDinCh1,int rangoDinCh2, int bins, int nShotsChk, int nSubChk, int delay) {
    /* configura la placa pasando el nùmero de canales, el entero por el que se divide la freq de adquisiciòn màxima.
    qFreqAdq 1, 2,3,.......,2^16
     rangoDin 0,1,2 equivale a +-0.2V +-2V y +-10V
     Además configura los buffers de la RAM a la que la placa transfire los datos aibuf1 y aibuf2.
     Configura triggres, bufferes de la placa. WD_AI_ContBufferSetup y WD_Buffer_Alloc
     inicia la adquisiciòn
    */


//variables placa
	I16 Id,Id2, card;//son requeridas por funciones de la placa para almacenar cosas. son de uso exclusivo de las funciones de la placa
	U16 card_type=PCIe_9852;
	U16 card_num=CARDNUM; //arranca en 0, en esta compu habìa dos placas la 0 y la 1.

	if ((card=WD_Register_Card (card_type, card_num)) <0 ) {
		printf("Register_Card error=%d", card);
		exit(1);
	}

	//WD_AI_AsyncDblBufferMode (card_num, TRUE);
	//----------------------------------
	// ai_buf y ai_buf2
	// configura los buffers de la ram donde se transfieren los datos de la placa
	int puntosChk=nCh*bins*nShotsChk/nSubChk;
	int tamBuffer =puntosChk*sizeof(I16);
    short* ai_buf = WD_Buffer_Alloc (card, tamBuffer);//direcciòn de memoria del buffer de la ram utilizado por la placa para descargar los datos.
   //lo tiene que utilizar el callback que vaya a buscar los datos por lo que tine que ser global. Hay un buffer en la ram por cada buffer en la placa.
   if(!ai_buf)
   {
	   printf("buffer1 allocation failed\n");
	   exit(1);
   }
  short* ai_buf2 = WD_Buffer_Alloc (card, tamBuffer);
   if(!ai_buf2)
   {
	   printf("buffer22 allocation failed\n");
	   WD_Buffer_Free (card, ai_buf);
	   exit(1);
   }
   //-----------------------------
//configura buffer en la placa


  I16 err=WD_AI_ContBufferSetup (card, ai_buf, puntosChk, &Id);
   if (err!=0) {
       printf("P9842_AI_ContBufferSetup 0 error=%d", err);
	   WD_Buffer_Free (card, ai_buf);
	   WD_Buffer_Free (card, ai_buf2);
	   WD_Release_Card(card);
       exit(1);
   }
   err=WD_AI_ContBufferSetup (card, ai_buf2, puntosChk, &Id2);
   if (err!=0) {
       printf("P9842_AI_ContBufferSetup 0 error=%d", err);
	   WD_AI_ContBufferReset (card);
	   WD_Buffer_Free (card, ai_buf);
	   WD_Buffer_Free (card, ai_buf2);
	   WD_Release_Card(card);
       exit(1);
   }


   // seteamos impedancia y rango dinàmico de los canales
   U16 rango1,rango2;
   switch(rangoDinCh1){
   case 0:
      rango1=AD_B_0_2_V;//+-200mV
      break;
   case 1:
       rango1=AD_B_2_V;//+-2V
       break;
   case 2:
        rango1=AD_B_10_V;//+-10V
   }
   switch(rangoDinCh2){
   case 0:
      rango2=AD_B_0_2_V;//+-200mV
      break;
   case 1:
       rango2=AD_B_2_V;//+-2V
       break;
   case 2:
        rango2=AD_B_10_V;//+-10V
   }

	WD_AI_CH_ChangeParam(card,-1,AI_IMPEDANCE,IMPEDANCE_50Ohm);/// card number,channel,channel setting,setting value
	WD_AI_CH_ChangeParam(card,0,AI_RANGE,rango1);/// card number,channel,setting,setting value
    WD_AI_CH_ChangeParam(card,1,AI_RANGE,rango2);
//----------------------------------------------------

//ver en el manual de la placa esta funciòn
   err = WD_AI_Config (card, TIMEBASE, 1, WD_AI_ADCONVSRC_TimePacer, 0, BUFAUTORESET);
   if (err!=0) {
       printf("WD_AI_Config error=%d", err);
	   WD_Buffer_Free (card, ai_buf);
	   WD_Buffer_Free (card, ai_buf2);
	   WD_Release_Card(card);
       exit(1);
   }
   //------------------------------------------
   //configuraciòn del trigger

   err = WD_AI_Trig_Config (card, ADTRIGMODE, ADTRIGSRC, ADTRIGPOL, 0, 0.0, 0, 0, delay, 0);
   if (err!=0) {
       printf("WD_AI_Trig_Config error=%d", err);
	   WD_Buffer_Free (card, ai_buf);
	   WD_Buffer_Free (card, ai_buf2);
	   WD_Release_Card(card);
       exit(1);
   }

//----------------------------------------------------
// Configura el callBack. El evento es que se llenó el buffer de la placa. TrigEvent haría otra cosa según el manual, pero con este funciona y con que sugiere el manual no
//el callback es el productor trae los datos del buffer de la ram reservado para la placa a los chunks. Por eso recibe tambièn los semàforos de los consumidores
    callback.bins=bins;
    callback.nCh=nCh;
    callback.nShotsChk=nShotsChk;
    callback.nSubChk=nSubChk;
    callback.cnt_SubChk = 0;
    callback.ai_buf=ai_buf;
    callback.ai_buf2=ai_buf2;
    callback.bufferActual=true;
    callback.chkActual=0;
    //callback.cambio_pozo=CreateEvent(NULL,false,false,NULL);
    //callback.pausa=false;
    //callback.contadorPozo=0;
//    DWORD pozoID;
//    _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))cambio_de_pozo,
//	0, 0, pozoID);
//inicializa disponible
    int i;
    for(i=0;i<CHUNKS;++i)callback.disponible[i]=true;
//----------------
//reserva memoria para  los chunks: short* chkBuffer

    // creamos semáforos
    callback.semConsumidor[0]=CreateSemaphore(NULL,0,CHUNKS,NULL);
    callback.semConsumidor[1]=CreateSemaphore(NULL,0,CHUNKS,NULL);
    callback.semConsumidor[2]=CreateSemaphore(NULL,0,CHUNKS,NULL);
    callback.semConsumidor[3]=CreateSemaphore(NULL,0,CHUNKS,NULL);
    callback.semConsumidor[4]=CreateSemaphore(NULL,0,CHUNKS,NULL);


	err = WD_AI_EventCallBack_x64(card, 1, TrigEvent, (U32) AI_CallBack);
	if (err!=0) {
		printf("WD_AI_EventCallBack error=%d", err);
		WD_AI_ContBufferReset (card);
		WD_Buffer_Free (card, ai_buf);
	    WD_Buffer_Free (card, ai_buf2);
		WD_Release_Card(card);
		exit(1);
	}

//--------------------------------------------
//start adquisition
    err = WD_AI_ContScanChannels(card, nCh-1, 0, bins, qFreqAdq, qFreqAdq, ASYNCH_OP); //aca puede ser read por scan

    if (err!=0) {
        printf("AI_ContScanChannels error=%d", err);
        WD_AI_ContBufferReset (card);
        WD_Buffer_Free (card, ai_buf);
	    WD_Buffer_Free (card, ai_buf2);
        WD_Release_Card(card);
        exit(1);
    }
}




void *raw_data_writer(void* n){

    int bins=(*(th_Data *)n).bins;
    int delay=(*(th_Data *)n).delay;
    int bins_raw=(*(th_Data *)n).bins_raw;
    int delay_raw=(*(th_Data *)n).delay_raw;
    int chunks_save=(*(th_Data *)n).chunks_save;
    int nShotsChk=(*(th_Data *)n).nShotsChk;
    int nCh=(*(th_Data *)n).nCh;
    int qFreq=(*(th_Data *)n).qFreq;
    long long nShots=(*(th_Data *)n).nShots;
    bool infinite_daq=(*(th_Data *)n).infinite_daq;
    char* fname_dir = (*(th_Data *)n).fname_dir;
    char* placa = (*(th_Data *)n).placa;
    bool rawsave_ch0 = (*(th_Data *)n).rawsave_ch0;
    bool rawsave_ch1 = (*(th_Data *)n).rawsave_ch1;
    bool rawsave = false;
    int nCh_copia = 0;

    int caso = 0;
    unsigned long long bin_copia=0; ///bines que copia por chunk
    if (rawsave_ch0){
        caso = 1;
        rawsave = true;
        //bin_copia += bins*nShotsChk;
        bin_copia += bins_raw*nShotsChk;
        nCh_copia++;
    }
    if (rawsave_ch1){
        caso = caso + 2;
        rawsave = true;
        //bin_copia += bins*nShotsChk;
        bin_copia += bins_raw*nShotsChk;
        nCh_copia++;
    }

    if (nCh == 1 && rawsave_ch0){
		//bin_copia = bins*nShotsChk;
		bin_copia = bins_raw*nShotsChk;
		rawsave = true;
        caso = 3;
        nCh_copia == 1;
    }

    if (nCh == 1 && rawsave_ch1){
		caso = 0;
		rawsave = false;
		printf("\n No se guarda Raw Data. Con un canal solo se adquiere el canal Ch0. \n");
    }

    printf("caso: %d //",caso);
    short* ch = malloc(nCh_copia*bins_raw*nShotsChk*sizeof(short));

//    if (nCh == 1 && rawsave_ch1){
//		caso = 0;
//		printf("No se guarda Raw Data. Con un canal solo se adquiere el canal Ch0. \n");
//    }

    char dire_ch0[70];
    char dire_ch0_hdr[70];

    /// Escribe el archivo y header
    DWORD bytesw=0;
    if (caso==1){
    strcpy(dire_ch0,fname_dir);
    strcat(dire_ch0,"/RAW_CH0");
    mkdir(dire_ch0);
    strcpy(dire_ch0_hdr,dire_ch0);
    strcat(dire_ch0_hdr,"/ch0.hdr");

    FILE* f_raw_data_out_ch0_h = fopen(dire_ch0_hdr, "ab");
        fprintf(f_raw_data_out_ch0_h,"Placa: '%s' \n",placa);
        fprintf(f_raw_data_out_ch0_h,"Dato: '%s' \n","RAW DATA");
        fprintf(f_raw_data_out_ch0_h,"DataType: '%s' \n","short");
        fprintf(f_raw_data_out_ch0_h,"PythonNpDataType: '%s' \n","np.int16");
        fprintf(f_raw_data_out_ch0_h,"BytesPerDatum: [%d] \n",2);
        fprintf(f_raw_data_out_ch0_h,"Bins: [%d] \n",bins);
        fprintf(f_raw_data_out_ch0_h,"Delay: [%d] \n",delay);
        fprintf(f_raw_data_out_ch0_h,"Bins_raw: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_ch0_h,"Delay_raw: [%d] \n",delay_raw);
        fprintf(f_raw_data_out_ch0_h,"Cols: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_ch0_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_raw_data_out_ch0_h,"NDatum: [%d] \n",1);
        fprintf(f_raw_data_out_ch0_h,"Channel: [%d] \n",0);
        fprintf(f_raw_data_out_ch0_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_raw_data_out_ch0_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_raw_data_out_ch0_h,"nShots: [%d] \n",nShots);
        fprintf(f_raw_data_out_ch0_h,"Fin header \n");
        fclose(f_raw_data_out_ch0_h);
    }

    char dire_ch1[70];
    char dire_ch1_hdr[70];

    if (caso==2){
    strcpy(dire_ch1,fname_dir);
    strcat(dire_ch1,"/RAW_CH1");
    mkdir(dire_ch1);
    strcpy(dire_ch1_hdr,dire_ch1);
    strcat(dire_ch1_hdr,"/ch1.hdr");

    FILE* f_raw_data_out_ch1_h = fopen(dire_ch1_hdr, "ab");
        fprintf(f_raw_data_out_ch1_h,"Placa: '%s' \n",placa);
        fprintf(f_raw_data_out_ch1_h,"Dato: '%s' \n","RAW DATA");
        fprintf(f_raw_data_out_ch1_h,"DataType: '%s' \n","short");
        fprintf(f_raw_data_out_ch1_h,"PythonNpDataType: '%s' \n","np.int16");
        fprintf(f_raw_data_out_ch1_h,"BytesPerDatum: [%d] \n",2);
        fprintf(f_raw_data_out_ch1_h,"Bins: [%d] \n",bins);
        fprintf(f_raw_data_out_ch1_h,"Delay: [%d] \n",delay);
        fprintf(f_raw_data_out_ch1_h,"Bins_raw: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_ch1_h,"Delay_raw: [%d] \n",delay_raw);
        fprintf(f_raw_data_out_ch1_h,"Cols: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_ch1_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_raw_data_out_ch1_h,"NDatum: [%d] \n",1);
        fprintf(f_raw_data_out_ch1_h,"Channel: [%d] \n",1);
        fprintf(f_raw_data_out_ch1_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_raw_data_out_ch1_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_raw_data_out_ch1_h,"nShots: [%d] \n",nShots);
        fprintf(f_raw_data_out_ch1_h,"Fin header \n");
        fclose(f_raw_data_out_ch1_h);
    }

    char dire_ch[70];
    char dire_ch_hdr[70];

    if (caso==3){
    strcpy(dire_ch,fname_dir);
    strcat(dire_ch,"/RAW_CH");
    mkdir(dire_ch);
    strcpy(dire_ch_hdr,dire_ch);
    strcat(dire_ch_hdr,"/ch.hdr");

    FILE* f_raw_data_out_h = fopen(dire_ch_hdr, "ab");
        fprintf(f_raw_data_out_h,"Placa: '%s' \n",placa);
        fprintf(f_raw_data_out_h,"Dato: '%s' \n","RAW DATA");
        fprintf(f_raw_data_out_h,"DataType: '%s' \n","short");
        fprintf(f_raw_data_out_h,"PythonNpDataType: '%s' \n","np.int16");
        fprintf(f_raw_data_out_h,"BytesPerDatum: [%d] \n",2);
        fprintf(f_raw_data_out_h,"Bins: [%d] \n",bins);
        fprintf(f_raw_data_out_h,"Delay: [%d] \n",delay);
        fprintf(f_raw_data_out_h,"Bins_raw: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_h,"Delay_raw: [%d] \n",delay_raw);
        fprintf(f_raw_data_out_h,"Cols: [%d] \n",bins_raw);
        fprintf(f_raw_data_out_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_raw_data_out_h,"NDatum: [%d] \n",nCh);
        fprintf(f_raw_data_out_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_raw_data_out_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_raw_data_out_h,"nShots: [%d] \n",nShots);
        fprintf(f_raw_data_out_h,"Fin header \n");
        fclose(f_raw_data_out_h);
        }

    char dire_time[70];
    char dire_time_hdr[70];

    if (rawsave){
    strcpy(dire_time,fname_dir);
    strcat(dire_time,"/TIME");
    mkdir(dire_time);
    strcpy(dire_time_hdr,dire_time);
    strcat(dire_time_hdr,"/time.hdr");

    FILE* f_time_out_h = fopen(dire_time_hdr, "ab");
        fprintf(f_time_out_h,"Placa: '%s' \n",placa);
        fprintf(f_time_out_h,"Dato: '%s' \n","Tiempo de escritura a disco");
        fprintf(f_time_out_h,"Comentario: '%s' \n","Tiempo de escritura a disco de un chunk de dato crudo con el fin de monitoreo");
        fprintf(f_time_out_h,"Bins: [%d] \n",bins);
        fprintf(f_time_out_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_time_out_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_time_out_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_time_out_h,"nShots: [%d] \n",nShots);
        fprintf(f_time_out_h,"Fin header \n");
        fclose(f_time_out_h);
        }


    long long shots_totales=0;
	int current_chunk=0; //current_chunk lleva la iteracion actual mod cant_max
	unsigned long long bin_move=bins*nShotsChk*nCh;
    int it_ovr=0; ///contador de iteraciones para situacion de overrun
    double velocidad;
    int i,j;
    int cnt_ch = 0;
    int cnt_ch_save = 0;

    char time_str[200];
    double tiempo;

    HANDLE f_raw_data_out_ch0_f;
    HANDLE f_raw_data_out_ch1_f;
    HANDLE f_raw_data_out_f;
    HANDLE f_time_out_f;

    char nombre_ch0[70];
    char nombre_ch1[70];
    char nombre_ch[70];
    char nombre_time[70];
    char num_str[10];

	while(salir == 0){ /// buscar mejor condicion de salida

		WaitForSingleObject(callback.semConsumidor[0], INFINITE); //espero si no hay datos

		if(callback.ovr){ ///OVR CHECK. Si no puedo seguir escribiendo, copio todos los datos del buffer.
			it_ovr++;
			if (it_ovr==CHUNKS-1){ ///si ya di toda la vuelta, termino
				break;
			}
			printf("Hay overrun \n");
		}

		cnt_ch++;

		StartCounter(); ///tiempo
		if (rawsave){
                if (caso == 1){

                    for (j=0;j<nShotsChk;++j){
                        for(i=0;i<bins_raw;++i){
                            ch[j*bins_raw+i] = chkBuffer[bin_move*current_chunk+j*bins*nCh+delay_raw*nCh+nCh*i];
                        }
                    }

                    if(cnt_ch%chunks_save == 1){

                            strcpy(nombre_ch0,dire_ch0);
                            strcat(nombre_ch0,"/");
                            sprintf(num_str, "%06d", cnt_ch_save);
                            strcat(nombre_ch0,num_str);
                            strcat(nombre_ch0,".bin");

                            f_raw_data_out_ch0_f = CreateFile(nombre_ch0,    // name of the file
                            GENERIC_WRITE, // open for writing
                            0,             // sharing mode, none in this case
                            0,             // use default security descriptor
                            CREATE_ALWAYS, // overwrite if exists
                            FILE_ATTRIBUTE_NORMAL,
                            0);
                    }


                    bytesw = 0;
                    WriteFile(f_raw_data_out_ch0_f,&ch[0],(long long)bin_copia*sizeof(short),&bytesw,NULL);///
                    FlushFileBuffers(f_raw_data_out_ch0_f);

                    if(cnt_ch%chunks_save == 0){
                        CloseHandle(f_raw_data_out_ch0_f);
                    }


                }else if(caso == 2){
                    for (j=0;j<nShotsChk;++j){
                        for(i=0;i<bins_raw;++i){
                            ch[j*bins_raw+i] = chkBuffer[bin_move*current_chunk+j*bins*nCh+delay_raw*nCh+nCh*i+1];
                        }
                    }

                    if(cnt_ch%chunks_save == 1){

                            strcpy(nombre_ch1,dire_ch1);
                            strcat(nombre_ch1,"/");
                            sprintf(num_str, "%06d", cnt_ch_save);
                            strcat(nombre_ch1,num_str);
                            strcat(nombre_ch1,".bin");

                            f_raw_data_out_ch1_f = CreateFile(nombre_ch1,    // name of the file
                            GENERIC_WRITE, // open for writing
                            0,             // sharing mode, none in this case
                            0,             // use default security descriptor
                            CREATE_ALWAYS, // overwrite if exists
                            FILE_ATTRIBUTE_NORMAL,
                            0);
                    }

                    bytesw = 0;
                    WriteFile(f_raw_data_out_ch1_f,&ch[0],(long long)bin_copia*sizeof(short),&bytesw,NULL);///
                    FlushFileBuffers(f_raw_data_out_ch1_f);

                    if(cnt_ch%chunks_save == 0){
                        CloseHandle(f_raw_data_out_ch1_f);
                    }

                }else if (caso == 3){
                    for (j=0;j<nShotsChk;++j){
                        for(i=0;i<bins_raw*nCh;++i){
                            ch[j*bins_raw*nCh+i] = chkBuffer[bin_move*current_chunk+j*bins*nCh+delay_raw*nCh+i];
                        }
                    }

                    if(cnt_ch%chunks_save == 1){

                            strcpy(nombre_ch,dire_ch);
                            strcat(nombre_ch,"/");
                            sprintf(num_str, "%06d", cnt_ch_save);
                            strcat(nombre_ch,num_str);
                            strcat(nombre_ch,".bin");

                            f_raw_data_out_f = CreateFile(nombre_ch,    // name of the file
                            GENERIC_WRITE, // open for writing
                            0,             // sharing mode, none in this case
                            0,             // use default security descriptor
                            CREATE_ALWAYS, // overwrite if exists
                            FILE_ATTRIBUTE_NORMAL,
                            0);
                    }


                    bytesw = 0;
                    WriteFile(f_raw_data_out_f,&ch[0],(long long)bin_copia*sizeof(short),&bytesw,NULL);///
                    FlushFileBuffers(f_raw_data_out_f);

                    if(cnt_ch%chunks_save == 0){
                        CloseHandle(f_raw_data_out_f);
                    }
                }


            if(bytesw < ((long long)bin_copia*sizeof(short))){
                salir_raw = true;
                printf("ERROR ESCRITURA");
                return n;
            }
		}
		tiempo=GetCounter();

		current_chunk++;
		callback.disponible[current_chunk-1]=true;

		/// Escribo archivo de tiempo
		if (rawsave){
            snprintf(time_str, sizeof(time_str),"Time: %f \n", tiempo);
            //bytesw=0;

                    if(cnt_ch%chunks_save == 1){

                            strcpy(nombre_time,dire_time);
                            strcat(nombre_time,"/");
                            sprintf(num_str, "%06d", cnt_ch_save);
                            strcat(nombre_time,num_str);
                            strcat(nombre_time,".time");

                            f_time_out_f = CreateFile(nombre_time,    // name of the file
                            GENERIC_WRITE, // open for writing
                            0,             // sharing mode, none in this case
                            0,             // use default security descriptor
                            CREATE_ALWAYS, // overwrite if exists
                            FILE_ATTRIBUTE_NORMAL,
                            0);

                            cnt_ch_save++;
                    }

            WriteFile(f_time_out_f,time_str, strlen(time_str),&bytesw,NULL);
            velocidad = ((double)bin_copia*sizeof(short)/1024.0/1024.0)/(tiempo/1000.0);
            //printf("velocidad de escritura: %f [Mb/seg] \n",((double)bin_copia*sizeof(short)/1024/1024)/(tiempo/1000));
            printf("velocidad de escritura: %f [Mb/seg] \n",velocidad);
            FlushFileBuffers(f_time_out_f);

            if(cnt_ch%chunks_save == 0){
                 CloseHandle(f_time_out_f);
            }

		}



		//printf("Escribi %d bytes en %.6fseg\n", bin_copia*2,tiempo/1000.0);
        shots_totales+=nShotsChk;

        if (!infinite_daq && shots_totales>=nShots){ /// deja de adqurir cuando llego hasta aca (puede haber adquirido mas shots que shot lim). puede guardar m?s datos que shot_lim (si no es multiplo de shots_per_chunk).
			break;
        }

		if (current_chunk==CHUNKS){//reinicio current_chunk
			current_chunk=0;
		}

	}

    if (rawsave){
        CloseHandle(f_time_out_f);
    }
    if (caso == 1){
        CloseHandle(f_raw_data_out_ch0_f);
    }
    if (caso == 2){
        CloseHandle(f_raw_data_out_ch1_f);
    }
    if (caso == 3){
        CloseHandle(f_raw_data_out_f);
    }
	salir_raw = true;
	salir = true; // por si hay overrun
    printf("Hilo RAW DATA terminado \n");
    return NULL;

}

void *procesa_osc(void* n){
    int bins=(*(th_Data *)n).bins;
    int delay=(*(th_Data *)n).delay;
    int nShotsChk=(*(th_Data *)n).nShotsChk;
    int nCh=(*(th_Data *)n).nCh;
    int qFreq=(*(th_Data *)n).qFreq;
    long long nShots=(*(th_Data *)n).nShots;
    bool infinite_daq=(*(th_Data *)n).infinite_daq;
    int window_time_osc=(*(th_Data *)n).window_time_osc;
    char* placa = (*(th_Data *)n).placa;
    int cant_curvas = (*(th_Data *)n).cant_curvas;

    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL);
    DWORD dwThreadPri = GetThreadPriority(GetCurrentThread());
    printf("Current thread priority is %d\n", dwThreadPri);

    float* procesado = malloc(bins*cant_curvas*sizeof(float)*nCh);

     /// VER EL TEMA DE LOS PIPES
    //int window=10;
    DWORD leido_paip;
    HANDLE paip = CreateNamedPipe(TEXT("\\\\.\\pipe\\Pipe3"),
                            PIPE_ACCESS_DUPLEX | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                            PIPE_WAIT,
                            1,
                            bins*sizeof(float)*cant_curvas*8,
                            bins*sizeof(float)*cant_curvas*8,
                            NMPWAIT_USE_DEFAULT_WAIT,
                            NULL);



    char command[100];
    //snprintf(command,100,"start cmd /k python test_marco1_m.py %d %d %d",perfil_mv_avg_size,window_bin,qFreq);
    snprintf(command,100,"start cmd /k python pipe_osciloscopio.py %d %d %d",bins,cant_curvas,qFreq);
    printf(command);
    system(command);

    short* chunk_actual=chkBuffer;
    int chunk_control=0;
    int i,k;

    while(salir == 0){


        WaitForSingleObject(callback.semConsumidor[4], INFINITE);


        memset(procesado,0,bins*cant_curvas*sizeof(float)*nCh);
//        memset(mean_w_ch1,0,bins*nShotsChk*sizeof(float));
//
//        for(i=0;i<bins*(window_time-1);++i){ ///calcula ventana-1
//            mean_w_ch0[i%bins]+=(float)(chunk_actual[i*nCh]);
//            mean_w_ch1[i%bins]+=(float)(chunk_actual[i*nCh+1]);
//        }
//
//        for(i=bins*(window_time-1);i<bins*window_time;++i){ ///termina ventana
//            mean_w_ch0[i%bins]=(mean_w_ch0[i%bins]+ (float)(chunk_actual[i*nCh]))/window_time;
//            mean_w_ch1[i%bins]=(mean_w_ch1[i%bins]+ (float)(chunk_actual[i*nCh+1]))/window_time;
//        }
//    //    printf("AndaPrimeraWindow\n");
//
//        for(i=bins*window_time;i<bins*nShotsChk;++i){///resta y suma el apropiado a la ventana calculada
//                mean_w_ch0[(i-bins*(window_time-1))]=mean_w_ch0[(i-bins*(window_time))]+((float)(chunk_actual[i*nCh])-(float)(chunk_actual[nCh*(i-bins*(window_time))]))/window_time;
//                mean_w_ch1[(i-bins*(window_time-1))]=mean_w_ch1[(i-bins*(window_time))]+((float)(chunk_actual[i*nCh+1])-(float)(chunk_actual[nCh*(i-bins*(window_time))+1]))/window_time;
//        }

        for (i=0;i<cant_curvas;++i){

                for (k=0;k<bins*window_time_osc;++k){
                    procesado[i*bins+k%bins] += ((float)chunk_actual[bins*nShotsChk/cant_curvas*i + nCh*k])/window_time_osc;
                    procesado[cant_curvas*bins + i*bins+k%bins] += ((float)chunk_actual[bins*nShotsChk/cant_curvas*i + nCh*k + 1])/window_time_osc;
                }
        }

         /// Pipe para graficar
        WriteFile(paip,&procesado[0],bins*cant_curvas*sizeof(float)*nCh,&leido_paip,NULL);

        chunk_control++;
        if(chunk_control==CHUNKS){// why??? deberia ser chunks??
            chunk_actual=chkBuffer;
            chunk_control=0;
        }else{
            chunk_actual+=bins*nShotsChk*nCh;//avanzo 2 channels
        }

    }


    CloseHandle(paip);
    free(procesado);
    salir_osc = true;
    printf("Hilo Osciloscopio terminado \n");
    return NULL;

}

void *procesa_STD(void* n){

    int bins=(*(th_Data *)n).bins;
    int delay=(*(th_Data *)n).delay;
    int nShotsChk=(*(th_Data *)n).nShotsChk;
    int chunks_save=(*(th_Data *)n).chunks_save;
    int nCh=(*(th_Data *)n).nCh;
    int qFreq=(*(th_Data *)n).qFreq;
    long long nShots=(*(th_Data *)n).nShots;
    bool infinite_daq=(*(th_Data *)n).infinite_daq;
    int window_time=(*(th_Data *)n).window_time;
    int window_bin=(*(th_Data *)n).window_bin;
    int window_bin_std=(*(th_Data *)n).window_bin_std;
    int window_bin_mean=(*(th_Data *)n).window_bin_mean;
    int bin_mon_edfa_i=(*(th_Data *)n).bin_mon_edfa_i;
    int bin_mon_edfa_f=(*(th_Data *)n).bin_mon_edfa_f;
    char* fname_dir = (*(th_Data *)n).fname_dir;
    char* placa = (*(th_Data *)n).placa;
    bool stdsave = (*(th_Data *)n).stdsave;
    bool normaliza_energia = (*(th_Data *)n).normaliza_energia;

    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL);
    DWORD dwThreadPri = GetThreadPriority(GetCurrentThread());
    printf("Current thread priority is %d\n", dwThreadPri);



    short* chunk_actual=chkBuffer;//arranco corrido 2 canales
    int i,j,k;

    int mean_mv_avg_size = bins - window_bin + 1 - window_bin_mean + 1;
    int std_mv_avg_size = mean_mv_avg_size;
    int std_mv_avg_avg_size = std_mv_avg_size - window_bin_std + 1;

    float* mean=malloc((bins-window_bin+1)*sizeof(float)); //falta free
    float* mean_w=malloc(bins*nShotsChk*sizeof(float));//falta free
    float* mean_w1=malloc((bins-window_bin+1)*(nShotsChk-window_time+1)*sizeof(float));//falta free
    float* std = malloc((bins-window_bin+1)*sizeof(float));
    float* mean_mv_avg = malloc(mean_mv_avg_size*sizeof(float));
    float* std_mv_avg = malloc(std_mv_avg_size*sizeof(float));
    float* std_mv_avg_avg = malloc(std_mv_avg_avg_size*sizeof(float));


    /// Escribe a archivo
    char dire_std[70];
    char dire_std_hdr[70];

    DWORD bytesw=0;
    if (stdsave){
        strcpy(dire_std,fname_dir);
        strcat(dire_std,"/STD");
        mkdir(dire_std);
        strcpy(dire_std_hdr,dire_std);
        strcat(dire_std_hdr,"/std.hdr");

        FILE* f_std_out_h=fopen(dire_std_hdr, "ab");
            fprintf(f_std_out_h,"Placa: '%s' \n",placa);
            fprintf(f_std_out_h,"Dato: '%s' \n","STD");
            fprintf(f_std_out_h,"DataType: '%s' \n","float");
            fprintf(f_std_out_h,"PythonNpDataType: '%s' \n","np.float32");
            fprintf(f_std_out_h,"BytesPerDatum: [%d] \n",4);
            fprintf(f_std_out_h,"Delay: [%d] \n",delay);
            fprintf(f_std_out_h,"Bins: [%d] \n",bins);
            fprintf(f_std_out_h,"Cols: [%d] \n",std_mv_avg_avg_size);
            fprintf(f_std_out_h,"NDatum: [%d] \n",1);
            fprintf(f_std_out_h,"NumberOfChannels: [%d] \n",nCh);
            fprintf(f_std_out_h,"FreqRatio: [%d] \n",qFreq);
            fprintf(f_std_out_h,"nShotsChk: [%d] \n",nShotsChk);
            fprintf(f_std_out_h,"nShots: [%d] \n",nShots);
            fprintf(f_std_out_h,"WindowTime: [%d] \n",window_time);
            fprintf(f_std_out_h,"WindowBin: [%d] \n",window_bin);
            fprintf(f_std_out_h,"WindowBin: [%d] \n",window_bin_std);
            fprintf(f_std_out_h,"WindowBinMean: [%d] \n",window_bin_mean);
            fprintf(f_std_out_h,"Fin header \n");
            fclose(f_std_out_h);
    }


        /// Escribe a archivo
    char dire_std_sn[70];
    char dire_std_hdr_sn[70];

    bytesw=0;
    if (stdsave){
        strcpy(dire_std_sn,fname_dir);
        strcat(dire_std_sn,"/STD_SN");
        mkdir(dire_std_sn);
        strcpy(dire_std_hdr_sn,dire_std_sn);
        strcat(dire_std_hdr_sn,"/std.hdr");

        FILE* f_std_out_h_sn=fopen(dire_std_hdr_sn, "ab");
            fprintf(f_std_out_h_sn,"Placa: '%s' \n",placa);
            fprintf(f_std_out_h_sn,"Dato: '%s' \n","STD");
            fprintf(f_std_out_h_sn,"DataType: '%s' \n","float");
            fprintf(f_std_out_h_sn,"PythonNpDataType: '%s' \n","np.float32");
            fprintf(f_std_out_h_sn,"BytesPerDatum: [%d] \n",4);
            fprintf(f_std_out_h_sn,"Delay: [%d] \n",delay);
            fprintf(f_std_out_h_sn,"Bins: [%d] \n",bins);
            fprintf(f_std_out_h_sn,"Cols: [%d] \n",bins-window_bin+1);
            fprintf(f_std_out_h_sn,"NDatum: [%d] \n",1);
            fprintf(f_std_out_h_sn,"NumberOfChannels: [%d] \n",nCh);
            fprintf(f_std_out_h_sn,"FreqRatio: [%d] \n",qFreq);
            fprintf(f_std_out_h_sn,"nShotsChk: [%d] \n",nShotsChk);
            fprintf(f_std_out_h_sn,"nShots: [%d] \n",nShots);
            fprintf(f_std_out_h_sn,"WindowTime: [%d] \n",window_time);
            fprintf(f_std_out_h_sn,"WindowBin: [%d] \n",window_bin);
            fprintf(f_std_out_h_sn,"WindowBin: [%d] \n",window_bin_std);
            fprintf(f_std_out_h_sn,"WindowBinMean: [%d] \n",window_bin_mean);
            fprintf(f_std_out_h_sn,"Fin header \n");
            fclose(f_std_out_h_sn);
    }

        /// Escribe a archivo
    char dire_mean[70];
    char dire_mean_hdr[70];

    bytesw=0;
    if (stdsave){
        strcpy(dire_mean,fname_dir);
        strcat(dire_mean,"/MEAN");
        mkdir(dire_mean);
        strcpy(dire_mean_hdr,dire_mean);
        strcat(dire_mean_hdr,"/mean.hdr");

        FILE* f_mean_out_h=fopen(dire_mean_hdr, "ab");
            fprintf(f_mean_out_h,"Placa: '%s' \n",placa);
            fprintf(f_mean_out_h,"Dato: '%s' \n","MEAN");
            fprintf(f_mean_out_h,"DataType: '%s' \n","float");
            fprintf(f_mean_out_h,"PythonNpDataType: '%s' \n","np.float32");
            fprintf(f_mean_out_h,"BytesPerDatum: [%d] \n",4);
            fprintf(f_mean_out_h,"Delay: [%d] \n",delay);
            fprintf(f_mean_out_h,"Bins: [%d] \n",bins);
            fprintf(f_mean_out_h,"Cols: [%d] \n",bins-window_bin+1);
            fprintf(f_mean_out_h,"NDatum: [%d] \n",1);
            fprintf(f_mean_out_h,"NumberOfChannels: [%d] \n",nCh);
            fprintf(f_mean_out_h,"FreqRatio: [%d] \n",qFreq);
            fprintf(f_mean_out_h,"nShotsChk: [%d] \n",nShotsChk);
            fprintf(f_mean_out_h,"nShots: [%d] \n",nShots);
            fprintf(f_mean_out_h,"WindowTime: [%d] \n",window_time);
            fprintf(f_mean_out_h,"WindowBin: [%d] \n",window_bin);
            fprintf(f_mean_out_h,"WindowBin: [%d] \n",window_bin_std);
            fprintf(f_mean_out_h,"WindowBinMean: [%d] \n",window_bin_mean);
            fprintf(f_mean_out_h,"Fin header \n");
            fclose(f_mean_out_h);
    }



    /// VER EL TEMA DE LOS PIPES
    //int window=10;
    DWORD leido_paip;
    HANDLE paip = CreateNamedPipe(TEXT("\\\\.\\pipe\\Pipe"),
                            PIPE_ACCESS_DUPLEX | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                            PIPE_WAIT,
                            1,
                            bins*sizeof(double)*CHUNKS,
                            bins*sizeof(double)*CHUNKS,
                            NMPWAIT_USE_DEFAULT_WAIT,
                            NULL);



    char command[100];
    //snprintf(command,100,"start cmd /k python test_marco1_m.py %d %d %d",perfil_mv_avg_size,window_bin,qFreq);
    snprintf(command,100,"start cmd /k python pipe_std.py %d %d %d",std_mv_avg_size,window_bin_std,qFreq);
    printf(command);
    system(command);

    int cnt_ch = 0;
    int cnt_ch_save = 0;

    double ttime=0.0;
    int chunk_control=0;

    HANDLE f_std_out_f;
    char nombre_std[70];

    HANDLE f_std_sn_out_f;
    char nombre_std_sn[70];

    HANDLE f_mean_out_f;
    char nombre_mean[70];
    char num_str[10];

    float* energia_edfa=malloc(nShotsChk*sizeof(float));
    memset(energia_edfa,1,nShotsChk*sizeof(float));
    float mean_energia = 1;
    int delta_bin_edfa = bin_mon_edfa_f-bin_mon_edfa_i;
    int off_e_edfa = 0;

    while(salir == 0){ ///wait podría estar aca

        cnt_ch++;
        //cnt_ch_norm++;

        WaitForSingleObject(callback.semConsumidor[1], INFINITE);
        //StartCounter();
    //    printf("HOLA\n");
        //StartCounter();

        /// Filtro 2D
        memset(mean,0,(bins-window_bin+1)*sizeof(float)); /// guarda la media
        memset(mean_w,0,bins*sizeof(float)); /// vector soporte
        memset(mean_w1,0,(bins-window_bin+1)*(nShotsChk-window_time+1)*sizeof(float)); /// dato crudo filtrado

        if (normaliza_energia){
            mean_energia = 0;
            for(i=0;i<nShotsChk;++i){
                    off_e_edfa = nCh*(i*bins + bin_mon_edfa_i);// para posicionar en el bin correspondiente del canal 1
                    energia_edfa[i] = (float)(chunk_actual[off_e_edfa + 1]/2) + (float)(chunk_actual[off_e_edfa + delta_bin_edfa*nCh + 1]/2);
                    for(j=1;j<delta_bin_edfa-1;++j){
                       energia_edfa[i] += (float)(chunk_actual[off_e_edfa + j*nCh+1]);
                    }
                    mean_energia += energia_edfa[i];
            }
            mean_energia = mean_energia/nShotsChk;
        }


        /// Primer shot
        for(i=0;i<bins*window_time;++i){ ///termina ventana
            mean_w[i%bins] +=(float)(chunk_actual[i*nCh]/energia_edfa[i/bins]*mean_energia);
        }

        for(i=0;i<window_bin;++i){
            mean_w1[0] += mean_w[i]/window_time/window_bin;
        }
        mean[0] = mean_w1[0]/(nShotsChk-window_time+1);

        for(i=1;i<bins-window_bin+1;++i){
            mean_w1[i] = mean_w1[i-1] + mean_w[i+window_bin-1]/window_time/window_bin - mean_w[i-1]/window_time/window_bin;
            mean[i] = mean_w1[i]/(nShotsChk-window_time+1);
        }


        for(i=1;i<nShotsChk-window_time+1;++i){

            for(j=0;j<window_bin;++j){
                mean_w[j] += -(float)(chunk_actual[(i-1)*bins*nCh + j*nCh])/energia_edfa[i-1]*mean_energia + (float)(chunk_actual[(i+window_time-1)*bins*nCh + j*nCh])/energia_edfa[i+window_time-1]*mean_energia;
                mean_w1[i*(bins-window_bin+1)] +=  mean_w[j]/window_time/window_bin;
            }
            mean[0] += mean_w1[i*(bins-window_bin+1)]/(nShotsChk-window_time+1);


            for(j=1;j<bins-window_bin+1;++j){
                mean_w[j+window_bin-1] += -(float)(chunk_actual[(i-1)*bins*nCh + (j+window_bin-1)*nCh])/energia_edfa[i-1]*mean_energia + (float)(chunk_actual[(i+window_time-1)*bins*nCh + (j+window_bin-1)*nCh])/energia_edfa[i+window_time-1]*mean_energia;
                mean_w1[i*(bins-window_bin+1) + j] = mean_w1[i*(bins-window_bin+1) + j - 1] - mean_w[j-1]/window_time/window_bin + mean_w[j+window_bin-1]/window_time/window_bin;
                mean[j] += mean_w1[i*(bins-window_bin+1) + j]/(nShotsChk-window_time+1);
            }

        }


        /// STD
        memset(std,0,(bins-window_bin+1)*sizeof(float));

        for(i=0;i<(nShotsChk-window_time+1)*(bins-window_bin+1);++i){
            std[i%(bins-window_bin+1)]+=(mean_w1[i]-mean[i%(bins-window_bin+1)])*(mean_w1[i]-mean[i%(bins-window_bin+1)]);
        }

        for(i=0;i<bins-window_bin+1;++i){
            std[i]=sqrt(std[i]/(nShotsChk-window_time));
        }

        /// Para normalizacion
        moving1avg(mean, bins-window_bin+1 ,window_bin_mean, mean_mv_avg, mean_mv_avg_size);

        for(i=0;i<mean_mv_avg_size;++i){
            std_mv_avg[i] =  std[i]/mean_mv_avg[i];
        }

        /// Moving average de STD
        moving1avg(std_mv_avg, std_mv_avg_size ,window_bin_std, std_mv_avg_avg, std_mv_avg_avg_size);


        /// Pipe para graficar
        WriteFile(paip,&std_mv_avg_avg[0],sizeof(float)*std_mv_avg_avg_size,&leido_paip,NULL);


        //20170111 agregamos esto para guardar a disco el vector procesado el archivo se abre y cierrra en main
        if (stdsave){
            bytesw = 0;

            if(cnt_ch%chunks_save == 1){

                    strcpy(nombre_std,dire_std);
                    strcat(nombre_std,"/");
                    sprintf(num_str, "%06d", cnt_ch_save);
                    strcat(nombre_std,num_str);
                    strcat(nombre_std,".std");

                    f_std_out_f = CreateFile(nombre_std,    // name of the file
                    GENERIC_WRITE, // open for writing
                    0,             // sharing mode, none in this case
                    0,             // use default security descriptor
                    CREATE_ALWAYS, // overwrite if exists
                    FILE_ATTRIBUTE_NORMAL,
                    0);

                    ///
                    strcpy(nombre_std_sn,dire_std_sn);
                    strcat(nombre_std_sn,"/");
                    strcat(nombre_std_sn,num_str);
                    strcat(nombre_std_sn,".std");

                    f_std_sn_out_f = CreateFile(nombre_std_sn,    // name of the file
                    GENERIC_WRITE, // open for writing
                    0,             // sharing mode, none in this case
                    0,             // use default security descriptor
                    CREATE_ALWAYS, // overwrite if exists
                    FILE_ATTRIBUTE_NORMAL,
                    0);


                    ///
                    strcpy(nombre_mean,dire_mean);
                    strcat(nombre_mean,"/");
                    strcat(nombre_mean,num_str);
                    strcat(nombre_mean,".std");

                    f_mean_out_f = CreateFile(nombre_mean,    // name of the file
                    GENERIC_WRITE, // open for writing
                    0,             // sharing mode, none in this case
                    0,             // use default security descriptor
                    CREATE_ALWAYS, // overwrite if exists
                    FILE_ATTRIBUTE_NORMAL,
                    0);

                    cnt_ch_save++;
            }

            WriteFile(f_std_out_f,&std_mv_avg_avg[0],std_mv_avg_avg_size*sizeof(float),&bytesw,NULL);
            FlushFileBuffers(f_std_out_f);

            WriteFile(f_std_sn_out_f,&std[0],(bins-window_bin+1)*sizeof(float),&bytesw,NULL);
            FlushFileBuffers(f_std_sn_out_f);

            WriteFile(f_mean_out_f,&mean[0],(bins-window_bin+1)*sizeof(float),&bytesw,NULL);
            FlushFileBuffers(f_mean_out_f);



            if(cnt_ch%chunks_save == 0){
                 CloseHandle(f_std_out_f);
            }

        }

        //printf("tiempo: %.5f \n",GetCounter()/1000.0);
        //printf("Termine STD \n");


        chunk_control++;
        if(chunk_control==CHUNKS){// why??? deberia ser chunks??
            chunk_actual=chkBuffer;
            chunk_control=0;
        }else{
            chunk_actual+=bins*nShotsChk*nCh;//avanzo 2 channels
        }

    }

    free(mean);
    free(mean_w);
    free(mean_w1);
    free(std);
    free(mean_mv_avg);
    free(std_mv_avg);
    free(std_mv_avg_avg);

    if (stdsave){
        CloseHandle(f_std_out_f);
    }


    CloseHandle(paip);
    salir_std = true;
    printf("Hilo STD terminado \n");
    return NULL;

}

void *procesa_Monitoreo(void* n){

    int bins=(*(th_Data *)n).bins;
    int delay=(*(th_Data *)n).delay;
    int nShotsChk=(*(th_Data *)n).nShotsChk;
    int chunks_save=(*(th_Data *)n).chunks_save;
    int nCh=(*(th_Data *)n).nCh;
    int qFreq=(*(th_Data *)n).qFreq;
    long long nShots=(*(th_Data *)n).nShots;
    bool infinite_daq=(*(th_Data *)n).infinite_daq;
    int window_time=(*(th_Data *)n).window_time;
    int window_bin=(*(th_Data *)n).window_bin;
    int bin_mon_laser_i=(*(th_Data *)n).bin_mon_laser_i;
    int bin_mon_laser_f=(*(th_Data *)n).bin_mon_laser_f;
    int bin_mon_edfa_i=(*(th_Data *)n).bin_mon_edfa_i;
    int bin_mon_edfa_f=(*(th_Data *)n).bin_mon_edfa_f;
    int window_mon_time=(*(th_Data *)n).window_mon_time;
    char* fname_dir = (*(th_Data *)n).fname_dir;
    char* placa = (*(th_Data *)n).placa;
    bool mon_edfa_save = (*(th_Data *)n).mon_edfa_save;
    bool mon_laser_save = (*(th_Data *)n).mon_laser_save;
    float cLaser=(*(th_Data *)n).cLaser;
    float cEDFA=(*(th_Data *)n).cEDFA;

    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL);
    DWORD dwThreadPri = GetThreadPriority(GetCurrentThread());
    printf("Current thread priority is %d\n", dwThreadPri);


    short* chunk_actual=chkBuffer;//arranco corrido 2 canales
    int i,j,k;
   // float *raw=malloc(bin*shots_per_chunk*sizeof(float));//falta free
    float* mean_dbl=malloc(bins*sizeof(double));//falta free
    float* mean_flt=malloc(bins*sizeof(float)); //falta free


        // AGREGA MARCO PARA VER ESTABILIDAD DE LA ENERGÍA DE LOS PULSOS AMPLIFICADOS
        // 11/01/2017 Histograma
        // Laser
        int delta_bin_laser = bin_mon_laser_f-bin_mon_laser_i;
        int off_e_laser = 0;
        int energia_avg_size = nShotsChk - window_mon_time + 1;
        int energia_avg_size_r = nShotsChk/window_mon_time;
        float* energia_laser=malloc(nShotsChk*sizeof(float));
        float* energia_avg_laser=malloc(energia_avg_size*sizeof(float));
        float* energia_avg_r_laser = malloc(energia_avg_size_r*sizeof(float));

        memset(energia_laser,0,nShotsChk*sizeof(float));
        memset(energia_avg_laser,0,energia_avg_size*sizeof(float));
        memset(energia_avg_r_laser,0,energia_avg_size_r*sizeof(float));

        // Edfa
        int delta_bin_edfa = bin_mon_edfa_f-bin_mon_edfa_i;
        int off_e_edfa = 0;
        float* energia_edfa=malloc(nShotsChk*sizeof(float));
        float* energia_avg_edfa=malloc(energia_avg_size*sizeof(float));
        float* energia_avg_r_edfa = malloc(energia_avg_size_r*sizeof(float));

        memset(energia_edfa,0,nShotsChk*sizeof(float));
        memset(energia_avg_edfa,0,energia_avg_size*sizeof(float));
        memset(energia_avg_r_edfa,0,energia_avg_size_r*sizeof(float));

        int super_vector_size = bins + 2*energia_avg_size_r;
        float* super_vector=malloc(super_vector_size*sizeof(float));
        memset(super_vector,0,super_vector_size*sizeof(float));
        //

    /// Escribe a archivo
    char dire_mon_laser[70];
    char dire_mon_laser_hdr[70];

    DWORD bytesw = 0;
    if (mon_laser_save){
    strcpy(dire_mon_laser,fname_dir);
    strcat(dire_mon_laser,"/MON_LASER");
    mkdir(dire_mon_laser);
    strcpy(dire_mon_laser_hdr,dire_mon_laser);
    strcat(dire_mon_laser_hdr,"/laser.mon.hdr");


    FILE* f_monitoreo_out_laser_h=fopen(dire_mon_laser_hdr, "ab");
        fprintf(f_monitoreo_out_laser_h,"Placa: '%s' \n",placa);
        fprintf(f_monitoreo_out_laser_h,"Dato: '%s' \n","Energia Pulsos LASER para Monitoreo");
        fprintf(f_monitoreo_out_laser_h,"Comentario: '%s' \n","Calcula la energia del pulso (laser o EDFA) como la integral de la senial del fotodiodo entre BinMonIni y BinMonFin");
        fprintf(f_monitoreo_out_laser_h,"DataType: '%s' \n","float");
        fprintf(f_monitoreo_out_laser_h,"PythonNpDataType: '%s' \n","np.float32");
        fprintf(f_monitoreo_out_laser_h,"BytesPerDatum: [%d] \n",4);
        fprintf(f_monitoreo_out_laser_h,"Delay: [%d] \n",delay);
        fprintf(f_monitoreo_out_laser_h,"Bins: [%d] \n",bins);
        //fprintf(f_monitoreo_out_laser_h,"Cols: [%d] \n",energia_avg_size_r);
        fprintf(f_monitoreo_out_laser_h,"Cols: [%d] \n",nShotsChk);
        fprintf(f_monitoreo_out_laser_h,"NDatum: [%d] \n",1);
        fprintf(f_monitoreo_out_laser_h,"BinMonIni: [%d] \n",bin_mon_laser_i);
        fprintf(f_monitoreo_out_laser_h,"BinMonFin: [%d] \n",bin_mon_laser_f);
        fprintf(f_monitoreo_out_laser_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_monitoreo_out_laser_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_monitoreo_out_laser_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_monitoreo_out_laser_h,"nShots: [%d] \n",nShots);
        fprintf(f_monitoreo_out_laser_h,"WindowTime: [%d] \n",window_time);
        fprintf(f_monitoreo_out_laser_h,"WindowBin: [%d] \n",window_bin);
        fprintf(f_monitoreo_out_laser_h,"Fin header \n");
        fclose(f_monitoreo_out_laser_h);
    }

    char dire_mon_edfa[70];
    char dire_mon_edfa_hdr[70];

    if (mon_edfa_save){
    strcpy(dire_mon_edfa,fname_dir);
    strcat(dire_mon_edfa,"/MON_EDFA");
    mkdir(dire_mon_edfa);
    strcpy(dire_mon_edfa_hdr,dire_mon_edfa);
    strcat(dire_mon_edfa_hdr,"/laser.mon.hdr");

    FILE* f_monitoreo_out_edfa_h=fopen(dire_mon_edfa_hdr, "ab");
        fprintf(f_monitoreo_out_edfa_h,"Placa: '%s' \n",placa);
        fprintf(f_monitoreo_out_edfa_h,"Dato: '%s' \n","Energia Pulsos EDFA para Monitoreo");
        fprintf(f_monitoreo_out_edfa_h,"Comentario: '%s' \n","Calcula la energia del pulso (laser o EDFA) como la integral de la senial del fotodiodo entre BinMonIni y BinMonFin");
        fprintf(f_monitoreo_out_edfa_h,"DataType: '%s' \n","float");
        fprintf(f_monitoreo_out_edfa_h,"PythonNpDataType: '%s' \n","np.float32");
        fprintf(f_monitoreo_out_edfa_h,"BytesPerDatum: [%d] \n",4);
        fprintf(f_monitoreo_out_edfa_h,"Delay: [%d] \n",delay);
        fprintf(f_monitoreo_out_edfa_h,"Bins: [%d] \n",bins);
        //fprintf(f_monitoreo_out_edfa_h,"Cols: [%d] \n",energia_avg_size_r);
        fprintf(f_monitoreo_out_edfa_h,"Cols: [%d] \n",nShotsChk);
        fprintf(f_monitoreo_out_edfa_h,"NDatum: [%d] \n",1);
        fprintf(f_monitoreo_out_edfa_h,"BinMonIni: [%d] \n",bin_mon_edfa_i);
        fprintf(f_monitoreo_out_edfa_h,"BinMonFin: [%d] \n",bin_mon_edfa_f);
        fprintf(f_monitoreo_out_edfa_h,"NumberOfChannels: [%d] \n",nCh);
        fprintf(f_monitoreo_out_edfa_h,"FreqRatio: [%d] \n",qFreq);
        fprintf(f_monitoreo_out_edfa_h,"nShotsChk: [%d] \n",nShotsChk);
        fprintf(f_monitoreo_out_edfa_h,"nShots: [%d] \n",nShots);
        fprintf(f_monitoreo_out_edfa_h,"WindowTime: [%d] \n",window_time);
        fprintf(f_monitoreo_out_edfa_h,"WindowBin: [%d] \n",window_bin);
        fprintf(f_monitoreo_out_edfa_h,"Fin header \n");
        fclose(f_monitoreo_out_edfa_h);
    }


    ///


    /// Pipe
    DWORD leido_paip;
    HANDLE paip = CreateNamedPipe(TEXT("\\\\.\\pipe\\Pipe2"),
                            PIPE_ACCESS_DUPLEX | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                            PIPE_WAIT,
                            1,
//                            bin*sizeof(double)*2,
//                            bin*sizeof(double)*2,
                            super_vector_size*sizeof(double)*20,
                            super_vector_size*sizeof(double)*20,
                            NMPWAIT_USE_DEFAULT_WAIT,
                            NULL);

    char command[100];
    snprintf(command,100,"start python pipe_monitoreo.py %d %d %d %d %d %d %d %f %f",bins,energia_avg_size_r,energia_avg_size_r,bin_mon_laser_i,bin_mon_laser_f,bin_mon_edfa_i,bin_mon_edfa_f,cLaser,cEDFA);
    printf(command);
    system(command);

    int cnt_ch = 0;
    int cnt_ch_save_l = 0;
    int cnt_ch_save_e = 0;

    int chunk_control=0;

    HANDLE f_monitoreo_out_laser_f;
    HANDLE f_monitoreo_out_edfa_f;
    char nombre_mon_laser[70];
    char nombre_mon_edfa[70];
    char num_str[10];

    while(salir == 0){ ///wait podría estar aca

        cnt_ch++;

        WaitForSingleObject(callback.semConsumidor[2], INFINITE);

        //StartCounter();
        memset(mean_dbl,0,bins*sizeof(double));
        memset(mean_flt,0,bins*sizeof(float));
       // win_actual=0;
     //   w_index=0;


        for(i=0;i<bins*nShotsChk;++i){///acumula
            mean_dbl[(i)%bins]+=(double)(chunk_actual[i*nCh+1]);//magia para no hacer 2 for
        }

        for(i=0;i<bins;++i){///divide
            mean_dbl[i]=mean_dbl[i]/(double)nShotsChk;
            mean_flt[i]=(float)(mean_dbl[i]);
            super_vector[i] = mean_flt[i]; // agrega Marco para estabilidad de pulsos
        }


      // AGREGA MARCO PARA VER ESTABILIDAD DE LA ENERGÍA DE LOS PULSOS AMPLIFICADOS
      // Sumo la senal con la regla de los trapecios.
      // Monitoreo LASER
        for(i=0;i<nShotsChk;++i){
                off_e_laser = nCh*(i*bins + bin_mon_laser_i);// para posicionar en el bin correspondiente del canal 1
                energia_laser[i] = (float)(chunk_actual[off_e_laser + 1]/2) + (float)(chunk_actual[off_e_laser + delta_bin_laser*nCh + 1]/2);
                for(j=1;j<delta_bin_laser-1;++j){
                   energia_laser[i] += (float)(chunk_actual[off_e_laser + j*nCh+1]);
                }

                off_e_edfa = 2*(i*bins + bin_mon_edfa_i);// para posicionar en el bin correspondiente del canal 1
                energia_edfa[i] = (float)(chunk_actual[off_e_edfa + 1]/2) + (float)(chunk_actual[off_e_edfa + delta_bin_edfa*nCh + 1]/2);
                for(j=1;j<delta_bin_edfa-1;++j){
                   energia_edfa[i] += (float)(chunk_actual[off_e_edfa + j*nCh+1]);
                }
        }

        // Aplico moving average del tamano de la ventana window
        moving1avg(energia_laser, nShotsChk ,window_mon_time, energia_avg_laser, energia_avg_size);
        moving1avg(energia_edfa, nShotsChk ,window_mon_time, energia_avg_edfa, energia_avg_size);

        //
        for (i=0;i<energia_avg_size_r;++i){
            energia_avg_r_laser[i] = energia_avg_laser[i*window_mon_time];
            energia_avg_r_edfa[i] = energia_avg_edfa[i*window_mon_time];
            }

        for(i=0;i<energia_avg_size_r;++i){
                super_vector[bins+i] = energia_avg_r_laser[i];
                super_vector[bins+energia_avg_size_r+i] = energia_avg_r_edfa[i];
        }

        //
        if (mon_laser_save){
            bytesw = 0;

            if(cnt_ch%chunks_save == 1){

                    strcpy(nombre_mon_laser,dire_mon_laser);
                    strcat(nombre_mon_laser,"/");
                    sprintf(num_str, "%06d", cnt_ch_save_l);
                    strcat(nombre_mon_laser,num_str);
                    strcat(nombre_mon_laser,".mon");

                    f_monitoreo_out_laser_f = CreateFile(nombre_mon_laser,    // name of the file
                    GENERIC_WRITE, // open for writing
                    0,             // sharing mode, none in this case
                    0,             // use default security descriptor
                    CREATE_ALWAYS, // overwrite if exists
                    FILE_ATTRIBUTE_NORMAL,
                    0);

                    cnt_ch_save_l++;
            }

            //WriteFile(f_monitoreo_out_laser_f,&energia_avg_r_laser[0],energia_avg_size_r*sizeof(float),&bytesw,NULL);
            WriteFile(f_monitoreo_out_laser_f,&energia_laser[0],nShotsChk*sizeof(float),&bytesw,NULL);
            FlushFileBuffers(f_monitoreo_out_laser_f);

            if(cnt_ch%chunks_save == 0){
                 CloseHandle(f_monitoreo_out_laser_f);
            }
        }
        if (mon_edfa_save){
            bytesw = 0;

            if(cnt_ch%chunks_save == 1){

                    strcpy(nombre_mon_edfa,dire_mon_edfa);
                    strcat(nombre_mon_edfa,"/");
                    sprintf(num_str, "%06d", cnt_ch_save_e);
                    strcat(nombre_mon_edfa,num_str);
                    strcat(nombre_mon_edfa,".mon");

                    f_monitoreo_out_edfa_f = CreateFile(nombre_mon_edfa,    // name of the file
                    GENERIC_WRITE, // open for writing
                    0,             // sharing mode, none in this case
                    0,             // use default security descriptor
                    CREATE_ALWAYS, // overwrite if exists
                    FILE_ATTRIBUTE_NORMAL,
                    0);

                    cnt_ch_save_e++;
            }

            //WriteFile(f_monitoreo_out_edfa_f,&energia_avg_r_edfa[0],energia_avg_size_r*sizeof(float),&bytesw,NULL);
            WriteFile(f_monitoreo_out_edfa_f,&energia_edfa[0],nShotsChk*sizeof(float),&bytesw,NULL);
            FlushFileBuffers(f_monitoreo_out_edfa_f);

            if(cnt_ch%chunks_save == 0){
                 CloseHandle(f_monitoreo_out_edfa_f);
            }

        }

        WriteFile(paip,&super_vector[0],sizeof(float)*super_vector_size,&leido_paip,NULL);



        chunk_control++;
        if(chunk_control==CHUNKS){// why??? deberia ser chunks??
            chunk_actual=chkBuffer;
            chunk_control=0;
        }else{
            chunk_actual+=bins*nShotsChk*2;//avanzo 2 channels
        }

    }


    if (mon_laser_save){
        CloseHandle(f_monitoreo_out_laser_f);
    }
    if (mon_edfa_save){
        CloseHandle(f_monitoreo_out_edfa_f);
    }
    CloseHandle(paip);
    free(super_vector);
    free(energia_avg_r_laser);
    free(energia_avg_r_edfa);
    free(energia_laser);
    free(energia_edfa);
    free(mean_flt);
    free(mean_dbl);

    salir_monitoreo = true;
    printf("Hilo Monitoreo terminado \n");
    return NULL;
}

void *procesa_FFT(void* n){

    int nCh=(*(th_Data *)n).nCh;
    int bins=(*(th_Data *)n).bins;
    int qFreq=(*(th_Data *)n).qFreq;
    int nShotsChk=(*(th_Data *)n).nShotsChk;
    int chunk_fft_salteo=(*(th_Data *)n).chunk_fft_salteo;
    int chunk_fft_promedio=(*(th_Data *)n).chunk_fft_promedio;
    int window_bin_std=(*(th_Data *)n).window_bin_std;
    int window_bin_mean=(*(th_Data *)n).window_bin_mean;
    int bin_mon_edfa_i=(*(th_Data *)n).bin_mon_edfa_i;
    int bin_mon_edfa_f=(*(th_Data *)n).bin_mon_edfa_f;
    bool normaliza_energia = (*(th_Data *)n).normaliza_energia;

    // Buffer float para fft
    int n_t=8;
    fftwf_init_threads();
    fftwf_plan_with_nthreads(n_t); ///COMPARAR CONTRA THREADS NORMALES, MKL, IPP, IPP_short

    /// Reservo memoria para salida y entrada del plan
    float* dst_float = malloc(sizeof(float)*bins*nShotsChk);
    fftwf_complex* out = fftwf_malloc(sizeof(fftwf_complex)*bins*(1+(nShotsChk/2)));
    float* out_abs = (float*)malloc(sizeof(float)*bins*(1+(nShotsChk/2))); // abs fft
    float* out_abs_acc = (float*)malloc(sizeof(float)*bins*(1+(nShotsChk/2))); // abs fft acumulada
    float* fft_0 = malloc(bins*sizeof(float));
    float* fft_0_mean = malloc(bins*sizeof(float));

    double tiempo;

    /// Calculo de bandas
    float* banda_a = malloc(bins*sizeof(float));
    float* banda_b = malloc(bins*sizeof(float));
    float* banda_c = malloc(bins*sizeof(float));

    float* banda_a_mvg = malloc((bins-window_bin_std+1)*sizeof(float));
    float* banda_b_mvg = malloc((bins-window_bin_std+1)*sizeof(float));
    float* banda_c_mvg = malloc((bins-window_bin_std+1)*sizeof(float));

    float* super_banda = malloc(3*(bins-window_bin_std+1)*sizeof(float));

    int banda_ai;
    int banda_af;
    int banda_bi;
    int banda_bf;
    int banda_ci;
    int banda_cf;

    /// Plan p2 fft: datos sin ordenar, luego fftw ordena
    int istride=1*bins;
    int ostride=1;
    int idist=1;
    int odist=1+nShotsChk/2;
    int nn = nShotsChk;
    fftwf_plan p2 = fftwf_plan_many_dft_r2c(1, &nn, bins,dst_float,NULL,istride, idist,out,NULL,ostride, odist, FFTW_MEASURE | FFTW_PRESERVE_INPUT);

    short* chunk_actual=chkBuffer;

    DWORD leido_paip;
    HANDLE paip = CreateNamedPipe(TEXT("\\\\.\\pipe\\PipeFFT"),
                            PIPE_ACCESS_DUPLEX | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                            PIPE_WAIT,
                            1,
                            bins*sizeof(float)*(1+(nShotsChk/2))*4,
                            bins*sizeof(float)*(1+(nShotsChk/2))*4,
                            NMPWAIT_USE_DEFAULT_WAIT,
                            NULL);

    char command[100];
    snprintf(command,100,"start python pipe_fft.py %d %d %d ",bins,nShotsChk,qFreq);
    printf(command);
    system(command);

    DWORD leido_paip_bandas;
    HANDLE paip_bandas = CreateNamedPipe(TEXT("\\\\.\\pipe\\PipeFFT_bandas"),
                            PIPE_ACCESS_DUPLEX | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                            PIPE_WAIT,
                            1,
                            (bins-window_bin_std+1)*sizeof(float)*8,
                            (bins-window_bin_std+1)*sizeof(float)*8,
                            NMPWAIT_USE_DEFAULT_WAIT,
                            NULL);

    char command1[100];
    snprintf(command1,100,"start python pipe_fft_bandas.py %d %d %d",bins-window_bin_std+1,qFreq, nShotsChk/2+1);
    printf(command1);
    system(command1);


    int cnt_salteo = 0;
    int cnt_promedio = 0;
    int chunk_control=0;
    int i,j;

    float* energia_edfa=malloc(nShotsChk*sizeof(float));
    memset(energia_edfa,1,nShotsChk*sizeof(float));
    int delta_bin_edfa = bin_mon_edfa_f-bin_mon_edfa_i;
    int off_e_edfa = 0;

    while(salir == 0){ ///wait podría estar aca

        WaitForSingleObject(callback.semConsumidor[3], INFINITE);

        cnt_salteo++;

        if (cnt_salteo%(chunk_fft_salteo+1) != 0){
            continue;
        }
        cnt_salteo = 0;

        StartCounter();

        if (normaliza_energia){
            for(i=0;i<nShotsChk;++i){
                    off_e_edfa = 2*(i*bins + bin_mon_edfa_i);// para posicionar en el bin correspondiente del canal 1
                    energia_edfa[i] = (float)(chunk_actual[off_e_edfa + 1]/2) + (float)(chunk_actual[off_e_edfa + delta_bin_edfa*nCh + 1]/2);
                    for(j=1;j<delta_bin_edfa-1;++j){
                       energia_edfa[i] += (float)(chunk_actual[off_e_edfa + j*nCh+1]);
                    }
            }
        }


        /// Casteo sin ordenar: la fftw ordena los datos.
        for (i=0;i<bins*nShotsChk*nCh;i+=nCh){
            dst_float[i/nCh] = (float)chunk_actual[i]/energia_edfa[i/bins/nCh];
        }


        fftwf_execute(p2);

        //printf("FFT: %f, %f, %f \n",out[2000*10+1][0],out[2000*10+2][0],out[2000*10+3][0]);

        /// Valor 0 de la fft
        for (i=0;i<bins;++i){
            fft_0[i] = sqrt(out[i*(nShotsChk/2+1)][0]*out[i*(nShotsChk/2+1)][0]+out[i*(nShotsChk/2+1)][1]*out[i*(nShotsChk/2+1)][1]);
        }

        moving1avg_full(fft_0,bins,window_bin_mean,fft_0_mean);


        /// Calcula el valor absoluto
        for(i=0;i<(( nShotsChk / 2 ) + 1)*bins;++i){
            out_abs[i]=sqrt(out[i][0]*out[i][0]+out[i][1]*out[i][1])/fft_0_mean[i/(nShotsChk/2+1)]*2; ///paralelizar
            if(isnan(out_abs[i])) out_abs[i]=0.0f;

            out_abs_acc[i] += out_abs[i];
        }

        /// Limites bandas
        banda_ai = bandas.banda_ai;
        banda_af = bandas.banda_af;
        banda_bi = bandas.banda_bi;
        banda_bf = bandas.banda_bf;
        banda_ci = bandas.banda_ci;
        banda_cf = bandas.banda_cf;

        /// Calculo de bandas
        memset(banda_a, 0, sizeof(float)*bins);
        memset(banda_b, 0, sizeof(float)*bins);
        memset(banda_c, 0, sizeof(float)*bins);

        memset(banda_a_mvg, 0, sizeof(float)*(bins-window_bin_std+1));
        memset(banda_b_mvg, 0, sizeof(float)*(bins-window_bin_std+1));
        memset(banda_c_mvg, 0, sizeof(float)*(bins-window_bin_std+1));

        for (j=0;j<bins;++j){

            for(i=banda_ai;i<banda_af;++i){
                banda_a[j] += out_abs[j*(nShotsChk/2+1) + (i+1)]/(float)(banda_af-banda_ai);
            }

            for(i=banda_bi;i<banda_bf;++i){
                banda_b[j] += out_abs[j*(nShotsChk/2+1) + (i+1)]/(float)(banda_bf-banda_bi);
            }

            for(i=banda_ci;i<banda_cf;++i){
                banda_c[j] += out_abs[j*(nShotsChk/2+1) + (i+1)]/(float)(banda_cf-banda_ci);
            }

        }

        moving1avg(banda_a, bins ,window_bin_std, banda_a_mvg, bins-window_bin_std+1);
        moving1avg(banda_b, bins ,window_bin_std, banda_b_mvg, bins-window_bin_std+1);
        moving1avg(banda_c, bins ,window_bin_std, banda_c_mvg, bins-window_bin_std+1);


        for (i=0;i<bins-window_bin_std+1;++i){
            super_banda[i] = banda_a_mvg[i];
            super_banda[i + bins-window_bin_std+1] = banda_b_mvg[i];
            super_banda[i + 2*(bins-window_bin_std+1)] = banda_c_mvg[i];
        }

        WriteFile(paip_bandas,&super_banda[0],sizeof(float)*(bins-window_bin_std+1)*3,&leido_paip_bandas,NULL);

        tiempo = GetCounter();
        printf("tiempo FFT: %.5f \n",tiempo/1000.0);



        cnt_promedio++;
        if (cnt_promedio%chunk_fft_promedio == 0){

                for (i=0;i<(( nShotsChk / 2 ) + 1)*bins;++i){
                    out_abs_acc[i] /= chunk_fft_promedio;
                }

            // Poner el pipe
            WriteFile(paip,&out_abs_acc[0],sizeof(float)*bins*(1+(nShotsChk/2)),&leido_paip,NULL);


            memset(out_abs_acc, 0, sizeof(float)*bins*(1+(nShotsChk/2)));
            cnt_promedio = 0;

        }
        printf("Termine FFT \n");

        chunk_control++;
        if(chunk_control==CHUNKS){// why??? deberia ser chunks??
            chunk_actual=chkBuffer;
            chunk_control=0;
        }else{
            chunk_actual+=bins*nShotsChk*nCh;//avanzo 2 channels
        }

    }


CloseHandle(paip);
free(dst_float);
free(out_abs);
free(out_abs_acc);
salir_fft = true;
printf("Hilo FFT terminado \n");
return NULL;

}


void* cambio_parametros(void* n){


    HANDLE pipeParametrosCWrite = CreateNamedPipe(TEXT("\\\\.\\pipe\\pipeParametrosCWrite"),
                                PIPE_ACCESS_OUTBOUND | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                                PIPE_WAIT,
                                1,
                                100,
                                100,
                                NMPWAIT_USE_DEFAULT_WAIT,
                                NULL);
    HANDLE pipeParametrosCRead = CreateNamedPipe(TEXT("\\\\.\\pipe\\pipeParametrosCRead"),
                                PIPE_ACCESS_INBOUND | PIPE_TYPE_BYTE | PIPE_READMODE_BYTE,   // FILE_FLAG_FIRST_PIPE_INSTANCE is not needed but forces CreateNamedPipe(..) to fail if the pipe already exists...
                                PIPE_WAIT,
                                1,
                                300,
                                300,
                                NMPWAIT_USE_DEFAULT_WAIT,
                                NULL);

     COMMTIMEOUTS comTimeOut;
     comTimeOut.ReadIntervalTimeout = 5000;


     BOOL to=SetCommTimeouts(
      pipeParametrosCRead,
      &comTimeOut
    );

    //printf("Variable de timeout: %d", to);

//    typedef struct COMMTIMEOUTS {
//      DWORD ReadIntervalTimeout;
//      DWORD ReadTotalTimeoutMultiplier;
//      DWORD ReadTotalTimeoutConstant;
//      DWORD WriteTotalTimeoutMultiplier;
//      DWORD WriteTotalTimeoutConstant;
//    } COMMTIMEOUTS_s;


    ConnectNamedPipe(pipeParametrosCRead,NULL);

    int* bandas_frec_write = malloc(6*sizeof(int));
    int* bandas_frec_read = malloc(6*sizeof(int));
    int cant_var = 6;

    char* buffer=calloc(42,sizeof(char));
    bool flag = true;

    while(salir == 0){

        //Sleep(1000);

        bandas_frec_write[0] = bandas.banda_ai;
        bandas_frec_write[1] = bandas.banda_af;
        bandas_frec_write[2] = bandas.banda_bi;
        bandas_frec_write[3] = bandas.banda_bf;
        bandas_frec_write[4] = bandas.banda_ci;
        bandas_frec_write[5] = bandas.banda_cf;

        DWORD leido_pipe,leido_pipe2;
        WriteFile(pipeParametrosCWrite,bandas_frec_write,sizeof(int)*6,&leido_pipe,NULL);
        ReadFile(pipeParametrosCRead,buffer,sizeof(char)*42,&leido_pipe2,NULL);

        //printf("%s \n",buffer);
        int i = 0;
        char *p = strtok (buffer, ",");
        char *array_read[cant_var];

        while (p != NULL)
        {
            array_read[i++] = p;
            p = strtok (NULL, ",");
        }

        WaitForSingleObject(pmut, INFINITE);
        bandas_frec_read[0] = atoi(array_read[0]);
        bandas_frec_read[1] = atoi(array_read[1]);
        bandas_frec_read[2] = atoi(array_read[2]);
        bandas_frec_read[3] = atoi(array_read[3]);
        bandas_frec_read[4] = atoi(array_read[4]);
        bandas_frec_read[5] = atoi(array_read[5]);
        ReleaseMutex(pmut);

        if (bandas.banda_ai != bandas_frec_read[0]) flag = true;
        if (bandas.banda_af != bandas_frec_read[1]) flag = true;
        if (bandas.banda_bi != bandas_frec_read[2]) flag = true;
        if (bandas.banda_bf != bandas_frec_read[3]) flag = true;
        if (bandas.banda_ci != bandas_frec_read[4]) flag = true;
        if (bandas.banda_cf != bandas_frec_read[5]) flag = true;

        if (flag){
            WaitForSingleObject(pmut, INFINITE);
            bandas.banda_ai = bandas_frec_read[0];
            bandas.banda_af = bandas_frec_read[1];
            bandas.banda_bi = bandas_frec_read[2];
            bandas.banda_bf = bandas_frec_read[3];
            bandas.banda_ci = bandas_frec_read[4];
            bandas.banda_cf = bandas_frec_read[5];

            ReleaseMutex(pmut);
        }

        flag = false;


    }

    CloseHandle(pipeParametrosCWrite);
    CloseHandle(pipeParametrosCRead);
    printf("Hilo Parametros terminado \n");
}




int main()
{


    /// CARGO PARAMETROS DE ADQUISICION ARCHIVO config.ini
    FILE* file_config = fopen("config.ini", "r"); /* should check the result */
    char line[200];
    char line_pozos[200];

    const char *P1_s = "'";
    const char *P2_s = "'";
    const char *P1_i = "[";
    const char *P2_i = "]";

    char *target = NULL;
    char *start, *end;

    char* name_pozos[10];
    char* placa;
    bool normaliza_energia = false;
    bool rawsave_ch0 = false;
    bool rawsave_ch1 = false;
    bool stdsave = false;
    bool mon_laser_save = false;
    bool mon_edfa_save = false;
    bool calcula_fft = false;
    bool calcula_osc = false;
    int bins;
    int nro_pozos = 0;
    int chunksPorPozo;
    int chunks_save;
    int nCh;
    int delay;
    int bins_raw;
    int delay_raw;
    short nShotsChk;
    short nSubChk;
    short qFreq;
    int window_time;
    int window_time_osc;
    int window_bin;
    int window_bin_std;
    int window_bin_mean;
    int bin_mon_laser_i;
    int bin_mon_laser_f;
    int bin_mon_edfa_i;
    int bin_mon_edfa_f;
    int cant_curvas = 0;
    float cLaser;
    float cEDFA;
    int chunk_fft_salteo;
    int chunk_fft_promedio;
    unsigned long long nShots = 0;
    bool infinite_daq = true;
    int i;

    while (fgets(line, sizeof(line), file_config)) {
            /* note that fgets don't strip the terminating \n, checking its
               presence would allow to handle lines longer that sizeof(line) */
            printf("%s", line);

        /// Busco string
        if (start=strstr(line,P1_s)){
            start += strlen(P1_s);
            if ( end = strstr( start,P2_s))
            {
                target = (char *)malloc(end-start+1);
                memcpy(target,start,end-start);
                target[end - start] = '\0';
            }
        }

        if (start=strstr(line,P1_i)){
            start += strlen(P1_i);
            if ( end = strstr( start,P2_i))
            {
                target = (char *)malloc(end-start+1);
                memcpy(target,start,end-start);
                target[end - start] = '\0';
            }
        }

        if (strstr(line,"Placa:")){
            placa = target;
        }
        if (strstr(line,"Bins:")){
            bins = atoi(target);
        }
        if (strstr(line,"Delay:")){
            delay = atoi(target);
        }
        if (strstr(line,"Bins_raw:")){
            bins_raw = atoi(target);
        }
        if (strstr(line,"Delay_raw:")){
            delay_raw = atoi(target);
        }
        if (strstr(line,"ChunksPorPozo:")){
            chunksPorPozo = atoi(target);
        }
        if (strstr(line,"ChunksSave:")){
            chunks_save = atoi(target);
        }
        if (strstr(line,"Nro. Pozos:")){
            nro_pozos = atoi(target);
            char* name_pozos[nro_pozos];
        }
        if (strstr(line,"NCh:")){
            nCh = atoi(target);
        }
        if (strstr(line,"NShotsChk:")){
            nShotsChk = atoi(target);
        }
        if (strstr(line,"NSubChk:")){
            nSubChk = atoi(target);
        }
        if (strstr(line,"WindowTime:")){
            window_time = atoi(target);
        }
        if (strstr(line,"WindowBin:")){
            window_bin = atoi(target);
        }
        if (strstr(line,"WindowBinSTD:")){
            window_bin_std = atoi(target);
        }
        if (strstr(line,"WindowBinMean:")){
            window_bin_mean = atoi(target);
        }
        if (strstr(line,"Bin_mon_laser_i:")){
            bin_mon_laser_i = atoi(target);
        }
        if (strstr(line,"Bin_mon_laser_f:")){
            bin_mon_laser_f = atoi(target);
        }
        if (strstr(line,"Bin_mon_edfa_i:")){
            bin_mon_edfa_i = atoi(target);
        }
        if (strstr(line,"Bin_mon_edfa_f:")){
            bin_mon_edfa_f = atoi(target);
        }
        if (strstr(line,"ChunkSalteoFFT:")){
            chunk_fft_salteo = atoi(target);
        }
        if (strstr(line,"ChunkPromedioFFT:")){
            chunk_fft_promedio = atoi(target);
        }
        if (strstr(line,"nShots:")){
            nShots = atoi(target);
        }
        if (strstr(line,"Calibracion_Laser:")){
            cLaser = atof(target);
        }
        if (strstr(line,"Calibracion_EDFA:")){
            cEDFA = atof(target);
        }
        if (strstr(line,"qFreq:")){
            qFreq = atoi(target);
        }
        for (i=0;i<nro_pozos;i++){
             snprintf(line_pozos, sizeof(line_pozos),"Pozo%d:",i+1);
             if (strstr(line,line_pozos)){
                name_pozos[i] = target;
            }
        }
        if (strstr(line,"NormalizaConEnergia:")){
            if(strstr(target,"si")){
                normaliza_energia = true;
            }
        }
        if (strstr(line,"GuardaRawDataCh0:")){
            if(strstr(target,"si")){
                rawsave_ch0 = true;
            }
        }
        if (strstr(line,"GuardaRawDataCh1:")){
            if(strstr(target,"si")){
                rawsave_ch1 = true;
            }
        }
        if (strstr(line,"GuardaSTDData:")){
            if(strstr(target,"si")){
                stdsave = true;
            }
        }
        if (strstr(line,"GuardaMonLaserData:")){
            if(strstr(target,"si")){
                mon_laser_save = true;
            }
        }
        if (strstr(line,"GuardaMonEdfaData:")){
            if(strstr(target,"si")){
                mon_edfa_save = true;
            }
        }
        if (strstr(line,"CalculaFFT:")){
            if(strstr(target,"si")){
                calcula_fft = true;
            }
        }

        if (strstr(line,"CalculaOSC:")){
            if(strstr(target,"si")){
                calcula_osc = true;
            }
        }

        if (strstr(line,"CantCurvasOsc:")){
            cant_curvas = atoi(target);
        }
        if (strstr(line,"WindowTimeOsc:")){
            window_time_osc = atoi(target);
        }
        target = NULL;

    }
    fclose(file_config);

    if (nShots>0){
        bool infinite_daq=false;
    }
    /// FIN DE LA CARGA
    if (nShotsChk%nSubChk != 0){
        printf("Error: NShotsChk/NSubChk debe ser un numero entero");
        salir = true;
    }


    /// Para los nombre de los archivos de salida
    char fname_dir[40];
	time_t rawtime;
	time (&rawtime);
	struct tm  *timeinfo = localtime (&rawtime);
	strftime(fname_dir, 50, "%y_%d_%m_%H_%M_%S", timeinfo);
	mkdir(fname_dir);

	/// Copio archivo de configuración en la carpeta de salida
	char config_file_dir[100];
	char fname_config;
	FILE *source, *dest;
	strcpy(config_file_dir,fname_dir);
	strcat(config_file_dir,"/config.ini");
	source = fopen("config.ini", "r");
	dest = fopen(config_file_dir, "w");
    while( ( fname_config = fgetc(source) ) != EOF )
       fputc(fname_config, dest);

    fclose(source);
    fclose(dest);

    /// Window time de monitoreo
    int window_mon_time = window_time;

    /// Aloca memoria del buffer
    chkBuffer=malloc((long long)bins*nShotsChk*nCh*CHUNKS*sizeof(short));
    //long tamanio=5L*1024L*1024L*1024L;
    printf("Puntero chunks reservado: %p.\n",chkBuffer);

    /// Struct con parametros de los threads
    th_Data DatosThread; // crea una estructura del tipo th_data
    DatosThread.bins=bins;
    DatosThread.nCh=nCh;
    DatosThread.delay=delay;
    DatosThread.nShotsChk=nShotsChk;
    DatosThread.nShots=nShots;
    DatosThread.qFreq=qFreq;
    DatosThread.infinite_daq=infinite_daq;
    DatosThread.window_time=window_time;
    DatosThread.window_bin=window_bin;
    DatosThread.window_bin_std=window_bin_std;
    DatosThread.window_bin_mean=window_bin_mean;

    DatosThread.bins_raw=bins_raw;
    DatosThread.delay_raw=delay_raw;

    DatosThread.bin_mon_laser_i=bin_mon_laser_i;
    DatosThread.bin_mon_laser_f=bin_mon_laser_f;
    DatosThread.bin_mon_edfa_i=bin_mon_edfa_i;
    DatosThread.bin_mon_edfa_f=bin_mon_edfa_f;
    DatosThread.cLaser=cLaser;
    DatosThread.cEDFA=cEDFA;
    DatosThread.window_mon_time=window_mon_time;

    DatosThread.chunk_fft_salteo=chunk_fft_salteo;
    DatosThread.chunk_fft_promedio=chunk_fft_promedio;

    DatosThread.placa = placa;
    DatosThread.fname_dir = fname_dir;

    DatosThread.chunks_save = chunks_save;
    DatosThread.normaliza_energia = normaliza_energia;
    DatosThread.rawsave_ch0 = rawsave_ch0;
    DatosThread.rawsave_ch1 = rawsave_ch1;
    DatosThread.stdsave = stdsave;
    DatosThread.mon_laser_save = mon_laser_save;
    DatosThread.mon_edfa_save = mon_edfa_save;

    DatosThread.cant_curvas = cant_curvas;
    DatosThread.window_time_osc = window_time_osc;

    bandas.banda_ai = 1;
    bandas.banda_af = 15;
    bandas.banda_bi = 15;
    bandas.banda_bf = 40;
    bandas.banda_ci = 40;
    bandas.banda_cf = 70;

    /*llama la funciòn adquirir desde donde se lanzan el productor y se setea el callback*/
    adquirir(nCh,qFreq,1,0,bins,nShotsChk,nSubChk,delay);
    /*lanza el proceso procesaDTS_01 (el consumidor)*/
        DWORD rawID, stdID, monID, fftID, oscID, cambioID;
        _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))raw_data_writer,
        (void*)&DatosThread, 0, (unsigned int *)&rawID);
         _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))procesa_STD,
        (void*)&DatosThread, 0, (unsigned int *)&stdID);
        if (nCh > 1){
         _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))procesa_Monitoreo,
        (void*)&DatosThread, 0, (unsigned int *)&monID);
        }
         _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))cambio_parametros,
        (void*)&DatosThread, 0, (unsigned int *)&cambioID);

        if (calcula_fft){
              _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))procesa_FFT,
            (void*)&DatosThread, 0, (unsigned int *)&fftID);
        }
        if (calcula_osc){
              _beginthreadex(NULL, 0, (unsigned int(__stdcall *)(void*))procesa_osc,
            (void*)&DatosThread, 0, (unsigned int *)&oscID);
        }
    /*--------------------------*/

    while(!kbhit() || getch() != 's') sleep(2);

    salir = true;

    while(salir_raw == 0) Sleep(1);
    while(salir_std == 0) Sleep(1);
    if (nCh > 1){
        while(salir_monitoreo == 0) Sleep(1);
    }
    if (calcula_fft){
        while(salir_fft == 0) Sleep(1);
    }
    if (calcula_osc){
        while(salir_osc == 0) Sleep(1);
    }

    CloseHandle(rawID);
    CloseHandle(stdID);
    if (nCh > 1){
        CloseHandle(monID);
    }
    CloseHandle(fftID);
    CloseHandle(oscID);

    free(chkBuffer);
    WD_Release_Card(0);

    return 0;
}
