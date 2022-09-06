import time#get timer library
import board#get rpi board library
import sys

#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
import adafruit_ina260#import sensor library
i2c = board.I2C()#set i2c pin for data input
cina260 = adafruit_ina260.INA260(i2c,0x41)#hook data input to this variable

charge = float(0)
timmer = int(0)
tmp1 = float(0)#record car battery capacity
tmp2 = float(0)#record home battery capacity
percent1=float(0)#record car battery percent
percent2=float(0)#record home battery percent
oc_counter=int(0)#counter to set when car is charged to that level
charge_need=float(0)#to save how many power is needed to charge the battery to that level from zero charge
to_charge=float(0)#to save how many power is needed to charge the battery to that level from program estimated car battery level
car_vol=float(0)#to detect car battery level with reading the car voltage

while (car_vol<2):#set to 2v incase detect some electric noise voltage, loop if not detect what we want   
    print("Connect vin+ pin from sensor to + terminal of the car battery, connect common ground to the - terminal of the battery . Do not connect charger yet")
    car_vol=cina260.voltage#sense voltage from lower end
    if(car_vol>4.13*2):
        tmp1=39960*2#fully charged
    if((car_vol>=4.1*2)&(car_vol<=4.13*2)):
        tmp1=39960*2*0.95#95percent
    if((car_vol<4.1*2)&(car_vol>=4.0*2)):
        tmp1=39960*2*0.9#90percent
    if((car_vol<4.0*2)&(car_vol>=3.9*2)):
        tmp1=39960*2*0.8#80percent
    if((car_vol<3.9*2)&(car_vol>=3.8*2)):
        tmp1=39960*2*0.7#70percent
    if((car_vol<3.8*2)&(car_vol>=3.75*2)):
        tmp1=39960*2*0.6#60percent
    if((car_vol>=3.72*2)&(car_vol<3.75*2)):
        tmp1=39960*2*0.45#45percent
    if((car_vol<3.72*2)&(car_vol>3.62*2)):
        tmp1=39960*2*0.4#40percent
    if((car_vol>=3.55*2)&(car_vol<3.62*2)):
        tmp1=39960*2*0.3#30percent
    if((car_vol>=3.5*2)&(car_vol<3.55*2)):
        tmp1=39960*2*0.2#20percent
    if((car_vol>=3.4*2)&(car_vol<3.5*2)):
        tmp1=39960*2*0.1#10percent
    if((car_vol>=3.3*2)&(car_vol<3.4*2)):
        tmp1=39960*2*0.05#5percent
    if((car_vol<3.3*2)&(car_vol>=3.2*2)):
        tmp1=39960*2*0.01#1percent,set to protect battery from over discharging
        
    elif((car_vol<3.2*2)):
        tmp1=0#1percent,set to protect battery from over discharging
        print("Car battery is dead or no battery detected :")#if the voltage is too low, print this
    print("Car battery level :",tmp1/39960/2*100,"%")#print how many percent the car battery estimate to have
    timmer = timmer +1
    if(timmer==5):#auto stop when long time without connection
        print()
        print("Detection system shut down due to inactive ")
        sys.exit('Detection system shut down')
    time.sleep(1)#detect every second
    
while True:
     with open('8dc.csv','w') as eight_w:#update battery charge level
        eight_w.write("{0:0.2f}".format(tmp1))#write
