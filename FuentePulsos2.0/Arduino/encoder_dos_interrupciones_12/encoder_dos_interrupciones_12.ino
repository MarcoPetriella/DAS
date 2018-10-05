


#include <DueFlashStorage.h>
DueFlashStorage dueFlashStorage;

#include <efc.h>
#include <flash_efc.h>
#include <Wire.h>
#include <Adafruit_MCP4725.h>
#include "SPI.h"
#include "Adafruit_GFX.h"
#include "Adafruit_ILI9340.h"
#include "math.h"

#if defined(__SAM3X8E__)
    #undef __FlashStringHelper::F(string_literal)
    #define F(string_literal) string_literal
#endif

// These are the pins used for the UNO
// for Due/Mega/Leonardo use the hardware SPI pins (which are different)
#define _sclk SCK
#define _miso MISO
#define _mosi MOSI
#define _cs 11
#define _dc 9
#define _rst 10

#define SERIAL_BUFFER_SIZE 128

// Para lectura de canales
int iter = 20;
int skip_num = 2;
int iter_ext = 1500;
int skip_num_ext = 20;
int n_chan = 12; 
int i = 0;
int j = 0;
int k = 0;
long m = 0;

int ana = 0;
long ana_sum = 0;
float ana_avg[12];
float ana_avg_ant[12];

int dummy = 0;
float dummyf = 0;


int val;
int encoder0PinA = 3;
int encoder0PinB = 2;
int encoder0PinC = 4;
int encoder0Pos = 0;
int encoder0PosAnt = 0;
int encoder0PinALast = LOW;
int n = LOW;

int pagina = 0;
int pagina_ant = 0;

int item_menu = 0;

int col_laser = LOW;
int laser_onoff = LOW;
int laser_onoff_ant = LOW;
float laser_tension = 1.30;
float paso_tension_laser = 0.01;
float laser_duracion = 100;
float laser_duracion_ant = 0;
float laser_frecuencia = 10000.0;
float laser_frecuencia_ant = 10000.0;
float paso_laser_frecuencia = 500.0;
int laser_ind = 0;
int laser_ind_ant = 0;
int item_laser = 0;
int digi_laser = 0;
int digi_laser_ant = 0;

int pin_laser_onoff = 49;
int pin_tec_onoff = 53;
int pin_tec_onoff_bl = 26;

int col_temperatura = LOW;
int tec_onoff = HIGH;
int tec_onoff_ant = HIGH;
float temp_setpoint = 16.55;
float temp_setpoint1 = 0.0;
float temp_laser_actual = 0.0;
float paso_temp_tec_laser = 0.01;

int tec_onoff_bl = HIGH;
int tec_onoff_bl_ant = HIGH;
float temp_setpoint_bl = 24.2;
float temp_setpoint_bl1 = 0.0;
float temp_bloque_actual = 0.0;
float paso_temp_tec_bloque = 0.10;


float rango_dac1 = 2.193;
float offset_dac1 = 0.551;
float rango_dac0 = 2.193;;
float offset_dac0 = 0.551;

float a_laser = 0.001129241;
float b_laser = 0.0002341077;
float c_laser = 0.00000008775468;
float tension_tec_laser = 1.;
float r_termistor_laser = 10000.;
float corriente_termistor_laser = 0.0001;
float corriente_tec_laser = 0.;
float offset_sensor_corriente_laser = 2.250;
float sensibilidad_sensor_corriente_laser = 1./0.185;
int digi_tec_laser = 0;
int digi_tec_laser_ant = 0;


Adafruit_MCP4725 dac_bl;
float a_bloque = 0.0011279;
float b_bloque = 0.00023429;
float c_bloque = 0.000000087298;
float tension_tec_bloque = 1.;
float r_termistor_bloque = 10000.;
float corriente_termistor_bloque = 0.0001;
float corriente_tec_bloque = 0.;
float offset_sensor_corriente_bloque = 2.250;
float sensibilidad_sensor_corriente_bloque = 1./0.185;
int digi_tec_bloque = 0;
int digi_tec_bloque_ant = 0;
float rango_dac_bl = 3.3;

float temp_laser = 23.0;
float temp_ambiente = 25.0;
float temp_ambiente1 = 25.0;
float corriente_tec = 0.345;
int item_temperatura = 0;

int parametros_onoff = 0;
int col_control = 0;
int item_control = 0;
int control_int_ext = 1;
float control_int_ext_f  = 1.;

// The struct of the configuration.
struct Configuration {
  int laser_onoff;
  float laser_tension;
  float laser_duracion;
  float laser_frecuencia;
  
  int tec_onoff;
  float temp_setpoint;
  int tec_onoff_bl;
  float temp_setpoint_bl;  
  
  int control_int_ext;
};

// initialize one struct
Configuration parametros_struct;

const int timeThreshold = 100;
const int timeThreshold1 = 500;
long timeCounter = 0;
volatile int ISRCounter = 6*7*5*5000;
volatile int clk = HIGH;
int ind_ini = 6*7*5*5000;
bool IsCW = true;

long t_loop = 0;
long t_evento = 0;
long delta_t = 0;
int flag_espera = 1;
int flag_pantalla = 0;
long t_espera = 40*1000; // en ms

bool read_ind = 0;
char serial_com[400];
int flag_hay_datos = 0;

float temp_amb1 = 0.;
float temp_amb2 = 0.;
float c1 = -8.72;
float m1 = 9.959;

// Using software SPI is really not suggested, its incredibly slow
//Adafruit_ILI9340 tft = Adafruit_ILI9340(_cs, _dc, _mosi, _sclk, _rst, _miso);
// Use hardware SPI
Adafruit_ILI9340 tft = Adafruit_ILI9340(_cs, _dc, _rst);


void setup() {
  Serial.begin(9600);
  dac_bl.begin(0x62);
  // put your setup code here, to run once:

  analogReadResolution(12);
  analogWriteResolution(12);
  pinMode (DAC0,OUTPUT);
  pinMode (DAC1,OUTPUT);



  pinMode(pin_laser_onoff, OUTPUT);     
  pinMode(pin_tec_onoff, OUTPUT); 
  pinMode(pin_tec_onoff_bl, OUTPUT); 
  
  pinMode(33, OUTPUT);     
  pinMode(31, OUTPUT); 
  pinMode(29, OUTPUT);   
  pinMode(27, OUTPUT);     
  pinMode(25, OUTPUT); 
  pinMode(23, OUTPUT);    

  pinMode(28, OUTPUT);  

  tft.begin();
  tft.setRotation(1);
  
  parametros_struct.laser_onoff = laser_onoff;
  parametros_struct.laser_tension = laser_tension;
  parametros_struct.laser_duracion = laser_duracion;
  parametros_struct.laser_frecuencia = laser_frecuencia;
  
  parametros_struct.tec_onoff = tec_onoff;
  parametros_struct.temp_setpoint = temp_setpoint;
  parametros_struct.tec_onoff = tec_onoff_bl;
  parametros_struct.temp_setpoint = temp_setpoint_bl;  
  
  parametros_struct.control_int_ext = control_int_ext;
  

  parametros_onoff = dueFlashStorage.read(0);
  if (parametros_onoff >= 1){
    parametros_onoff = 1;
    }
    //Serial.println(parametros_onoff);

  if ((parametros_onoff == 0)){
    //Serial.println("holacc");
    
    byte* b_array = dueFlashStorage.readAddress(4); // byte array which is read from flash at adress 4
    //Configuration parametros_struct;
    memcpy(&parametros_struct, b_array, sizeof(Configuration)); // copy byte array to temporary struct

    laser_onoff = parametros_struct.laser_onoff;
    laser_tension = parametros_struct.laser_tension;
    laser_duracion = parametros_struct.laser_duracion;
    laser_frecuencia = parametros_struct.laser_frecuencia;

    tec_onoff = parametros_struct.tec_onoff;
    temp_setpoint = parametros_struct.temp_setpoint;  	
    tec_onoff_bl = parametros_struct.tec_onoff_bl;
    temp_setpoint_bl = parametros_struct.temp_setpoint_bl;  
	control_int_ext = parametros_struct.control_int_ext;  
    //Serial.println(laser_tension);

  }
  
  
//  // Calibro DAC1
//  analogWrite(DAC1, 0);
//  delay(500);
//  for (i=0;i<100;i++){
//	  ana = analogRead(10); 
//	  ana_sum = ana_sum + ana;	  
//	  delay(50);
//  }
//  float di = ana_sum/100.;
//  di = di*3.3/4095.;
//  
//  ana = 0;
//  ana_sum = 0;
//  analogWrite(DAC1, 4095);
//  delay(500);
//  for (i=0;i<100;i++){
//	  ana = analogRead(10); 
//	  ana_sum = ana_sum + ana;
//	  delay(50);	  
//  }
//  float df = ana_sum/100.; 
//  df = df*3.3/4095.;
//  ana = 0;
//  ana_sum = 0;
//
//  rango_dac1 = df-di;
//  offset_dac1 = di;  
//  
//  rango_dac0 = df-di;
//  offset_dac0 = di;    
  

  
  // Seteo el trigger
  REG_PIOC_PDR = 0x3FC;  //B1111111100, PIO Disable Register
  REG_PIOC_ABSR = REG_PIOC_ABSR | 0x3FCu; //B1111111100, Peripheral AB Select Register
  REG_PMC_PCER1 = REG_PMC_PCER1 | 16; //Peripheral Clock Enable Register 1 (activate clock for PWM, id36, bit5 of PMC_PCSR1)
  REG_PWM_ENA = REG_PWM_SR | B1000; //PWM Enable Register | PWM Status Register (activate channels 0,1,2,3)
  REG_PWM_CMR3 = 0x10000; //Channe3 Mode Register: Dead Time Enable DTE=1
  REG_PWM_DT3 = 0xA800A8;   
  
	// Inicializo valores:
	// Laser on-off:
    if (laser_onoff == 0){
      digitalWrite(pin_laser_onoff, LOW);  
	}else{
      digitalWrite(pin_laser_onoff, HIGH);  
    } 		
	// Ancho de pulso:
	ancho_de_pulso_function(laser_duracion);  
	// Tension laser:
    digi_laser = round((laser_tension-offset_dac1)*float(pow(2,12))/rango_dac1);
    analogWrite(DAC1, digi_laser);
	// Laser frecuencia:
    laser_ind = round(84000000/laser_frecuencia);
	REG_PWM_CPRD3 = laser_ind;
	REG_PWM_CDTY3 = round(laser_ind*0.5);
	
	// TEC Laser on-off:
    if (tec_onoff == 0){
		digitalWrite(pin_tec_onoff, LOW); 	
	}else{
		digitalWrite(pin_tec_onoff, HIGH); 	
	}  	
	// Temperatura TEC Laser:
	r_termistor_laser = r_to_volt(temp_setpoint, a_laser, b_laser, c_laser);	
	tension_tec_laser = r_termistor_laser*corriente_termistor_laser;
	digi_tec_laser = (tension_tec_laser-offset_dac0)*float(pow(2,12))/rango_dac0;
	analogWrite(DAC0, digi_tec_laser);	

  // TEC Laser on-off:
    if (tec_onoff_bl == 0){
    digitalWrite(pin_tec_onoff_bl, LOW);   
  }else{
    digitalWrite(pin_tec_onoff_bl, HIGH);  
  }   
  // Temperatura TEC Laser:
  r_termistor_bloque = r_to_volt(temp_setpoint_bl, a_bloque, b_bloque, c_bloque);  
  tension_tec_bloque = r_termistor_bloque*corriente_termistor_bloque;
  digi_tec_bloque = tension_tec_bloque*float(pow(2,12))/rango_dac_bl;
  dac_bl.setVoltage(digi_tec_bloque, false);
  
  tec_onoff_ant = tec_onoff;
  tec_onoff_bl_ant = tec_onoff_bl;
  laser_onoff_ant = laser_onoff;
  digi_laser_ant = digi_laser;
  digi_tec_laser_ant = digi_tec_laser;
  digi_tec_bloque_ant = digi_tec_bloque;
  laser_duracion_ant = laser_duracion;
  laser_frecuencia_ant = laser_frecuencia;
  laser_ind_ant = laser_ind;
  

  

// if ((parametros_onoff) && (codeRunningForTheFirstTime == 0)){
//    b_array = dueFlashStorage.readAddress(2); // byte array which is read from flash at adress 4
//    Configuration parametros_struct; // create a temporary struct
//    memcpy(&parametros_struct, b_array, sizeof(Configuration)); // copy byte array to temporary struct
//   }
//  dueFlashStorage.write(0, 0); 
  

  
  // Lectura de canales
	for (k =0;k<n_chan;k++){
	  ana_avg[k] = 0.0;
	  }  
	  
	for (k =0;k<n_chan;k++){
	  ana_avg_ant[k] = 0.0;
	  } 	  
  
}

void loop() {
	

	
// control interno o externo
	
  digitalWrite(28, LOW);   
	  
	  
		

		if(Serial.available() >= 10){  
			// fill array
			//flag_hay_datos = 1;
			
			Serial.readBytes((char*)&read_ind, sizeof(read_ind));
			
			Serial.readBytes((char*)&laser_frecuencia, sizeof(laser_frecuencia));
			Serial.readBytes((char*)&laser_duracion, sizeof(laser_duracion));
			Serial.readBytes((char*)&laser_tension, sizeof(laser_tension));
			
 			Serial.readBytes((char*)&laser_onoff, sizeof(laser_onoff));
			
			Serial.readBytes((char*)&tec_onoff, sizeof(tec_onoff));
			Serial.readBytes((char*)&temp_setpoint, sizeof(temp_setpoint));     

			Serial.readBytes((char*)&tec_onoff_bl, sizeof(tec_onoff_bl));
			Serial.readBytes((char*)&temp_setpoint_bl, sizeof(temp_setpoint_bl));   

			Serial.readBytes((char*)&dummy, sizeof(dummy)); 
			//Serial.readBytes((char*)&iter_ext, sizeof(iter_ext)); 
			//Serial.readBytes((char*)&skip_num_ext, sizeof(skip_num_ext)); 

			digi_laser = round((laser_tension-offset_dac1)*float(pow(2,12))/rango_dac1);
			laser_ind = round(84000000/laser_frecuencia);

			r_termistor_laser = r_to_volt(temp_setpoint, a_laser, b_laser, c_laser);	
			tension_tec_laser = r_termistor_laser*corriente_termistor_laser;
			digi_tec_laser = (tension_tec_laser-offset_dac0)*float(pow(2,12))/rango_dac0;
			
			r_termistor_bloque = r_to_volt(temp_setpoint_bl, a_bloque, b_bloque, c_bloque);  
			tension_tec_bloque = r_termistor_bloque*corriente_termistor_bloque;
			digi_tec_bloque = tension_tec_bloque*float(pow(2,12))/rango_dac_bl;			

			
			
			//Serial.println(laser_duracion):

			
		}
	

		  // Medicion de los canales analogicos
		  
		  
 		  i = i + 1;
		  ana = analogRead(j); 
		  
		  if (i > skip_num_ext){
			ana_sum = ana_sum + ana;   
		  }
		  
		  
		  if (i == iter_ext){

			
			ana_avg[j] = ana_sum/(iter_ext-skip_num_ext)*3.3/4095.;
			ana_sum = 0;

				   
			i = 0;
			j = j + 1;

			if (j == n_chan){
				

				temp_laser_actual = r_to_temp(ana_avg[8]/corriente_termistor_laser,a_laser,b_laser,c_laser);
				temp_bloque_actual = r_to_temp(ana_avg[6]/corriente_termistor_bloque,a_bloque,b_bloque,c_bloque);
				temp_setpoint1 = r_to_temp(ana_avg[9]/corriente_termistor_laser,a_laser,b_laser,c_laser);
				temp_setpoint_bl1 = r_to_temp(ana_avg[7]/corriente_termistor_bloque,a_bloque,b_bloque,c_bloque);
				corriente_tec_laser = (ana_avg[1] - offset_sensor_corriente_laser)*sensibilidad_sensor_corriente_laser;
				corriente_tec_bloque = (ana_avg[3] - offset_sensor_corriente_bloque)*sensibilidad_sensor_corriente_bloque;
				temp_amb1 = (ana_avg[0]*1000-c1)/m1;
        temp_amb2 = (ana_avg[2]*1000-c1)/m1;
				control_int_ext_f = 1.0;
				
			  delay(200);	
			  sprintf(serial_com, "%d, %f ,%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f    \n",true, temp_amb1, corriente_tec_laser, temp_amb2, corriente_tec_bloque, ana_avg[4], ana_avg[5], temp_bloque_actual, temp_setpoint_bl1, temp_laser_actual, temp_setpoint1, 1000.*ana_avg[10], ana_avg[11], control_int_ext_f);
			 Serial.write(serial_com);
			 Serial.flush();
			  delay(500);
			  
			  j = 0;
			  for (k = 0;k<n_chan;k++){
				 ana_avg[k] = 0.0;
			  }
    
			  
			}
		  }
		  

		//digitalWrite(pin_laser_onoff, HIGH);    
		// Laser frecuencia:
		// Inicializo valores:
		// Laser on-off:
		if (laser_onoff_ant != laser_onoff){
			if (laser_onoff == 0){
			  digitalWrite(pin_laser_onoff, LOW);  
			}else{
			  digitalWrite(pin_laser_onoff, HIGH);  
			} 	
		}		
		// Ancho de pulso:
		if (laser_duracion_ant != laser_duracion){
			ancho_de_pulso_function(laser_duracion);  
		}
		// Tension laser:
		if (digi_laser_ant != digi_laser){
			//digi_laser = round((laser_tension-offset_dac1)*float(pow(2,12))/rango_dac1);
			analogWrite(DAC1, digi_laser);
			// Laser frecuencia:
		}	
		
		if (laser_ind_ant != laser_ind){
			laser_ind = round(84000000/laser_frecuencia);
			REG_PWM_CPRD3 = laser_ind;
			REG_PWM_CDTY3 = round(laser_ind*0.5);
		}
		
		// TEC Laser on-off:
		if (tec_onoff_ant != tec_onoff){
			if (tec_onoff == 0){
				digitalWrite(pin_tec_onoff, LOW); 	
			}else{
				digitalWrite(pin_tec_onoff, HIGH); 	
			}  	
		}
		// Temperatura TEC Laser:
		if (digi_tec_laser_ant != digi_tec_laser){
			analogWrite(DAC0, digi_tec_laser);	
		}
		
		// TEC Bloque on-off:
		if (tec_onoff_bl_ant != tec_onoff_bl){
			if (tec_onoff_bl == 0){
			digitalWrite(pin_tec_onoff_bl, LOW);   
		  }else{
			digitalWrite(pin_tec_onoff_bl, HIGH);  
		  } 
		// Temperatura TEC Bloque: 
		}
		if (digi_tec_bloque_ant != digi_tec_bloque){
		  dac_bl.setVoltage(digi_tec_bloque, false);
		}
		
		
		  tec_onoff_ant = tec_onoff;
		  tec_onoff_bl_ant = tec_onoff_bl;
		  laser_onoff_ant = laser_onoff;
		  digi_laser_ant = digi_laser;
		  digi_tec_laser_ant = digi_tec_laser;
		  digi_tec_bloque_ant = digi_tec_bloque;
		  laser_duracion_ant = laser_duracion;
		  laser_frecuencia_ant = laser_frecuencia;		
	
		
	
}



void ancho_de_pulso_function (int laser_duracion){

			int ancho_pulso_ind = floor((laser_duracion -10.)/320.*64.);

			int val1 = ancho_pulso_ind/2;
			int res1 = ancho_pulso_ind%2;
			
			int val2 = val1/2;
			int res2 = val1%2;
			
			int val3 = val2/2;
			int res3 = val2%2;
			
			int val4 = val3/2;
			int res4 = val3%2;  
				
			int val5 = val4/2;
			int res5 = val4%2;
			
			int val6 = val5/2;
			int res6 = val5%2;    
			
			  if (res6 == 0){
				digitalWrite(33, LOW);
			  }else{
				digitalWrite(33, HIGH);
				}
				
			  if (res5 == 0){
				digitalWrite(31, LOW);
			  }else{
				digitalWrite(31, HIGH);
				}
				
			  if (res4 == 0){
				digitalWrite(29, LOW);
			  }else{
				digitalWrite(29, HIGH);
				}
				
			  if (res3 == 0){
				digitalWrite(27, LOW);
			  }else{
				digitalWrite(27, HIGH);
				}
				
			  if (res2 == 0){
				digitalWrite(25, LOW);
			  }else{
				digitalWrite(25, HIGH);
				}
				
			  if (res1 == 0){
				digitalWrite(23, LOW);
			  }else{
				digitalWrite(23, HIGH);
				}   

}

float r_to_volt(float temp,float a, float b, float c){
	
	temp = (double)temp + 273.1;
	a = (double)a;
	b = (double)b;
	c = (double)c;
	
	double x = 1./c*(a - 1./temp);  
	double y = sqrt(pow(b/3/c,3) + pow(x/2,2));
	double r = exp(pow(y-x/2.,1./3.) - pow(y+x/2.,1./3.));
	r = (float) r;
	
	return r;
}


float r_to_temp(float r,float a, float b, float c){

	r = (double)r;
	a = (double)a;
	b = (double)b;
	c = (double)c;	
	
	double temp = a + b*log(r) + c*pow(log(r) ,3);
	temp = 1./temp;
	
	temp = temp - 273.1;
	temp = (float)temp;
		
	return temp;
}
