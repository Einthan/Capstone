import time #get timer library
import board    #get rpi board library
import sys

import adafruit_ina260#import sensor library
#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
i2c = board.I2C()#set i2c pin for data input
hina260 = adafruit_ina260.INA260(i2c,0x40)#hook data input to this variable

consume = float(0)  #define discharge total watt
tmp2 = float(0)#define charge level for 12v battery

command = input("If the home battery is charging by the solar pannel, type c; If using the home battery as source, type d :")
if(command !='c') & (command !='d'):
    print("What you want again?")
    sys.exit()
    
with open('12.csv','r') as twelve_r: #open the pervious stroed 12 capacity data
    data = float(twelve_r.read()) #read data into float
    print("Wattage ",data)#print how many charge left
    tmp2=float(data)#set temporary charge level to tmp2
    
while True:#triigger when sensor is connected to the battery and reads data
    from datetime import datetime#get time module

    now = datetime.now()#get date, time now

    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)) #print the date, time now
    
    if("d" in command):

        consume = consume + (hina260.power)/1000 #calculate power consumption in W every second
        tmp2 = tmp2 - (hina260.power/1000)#total power decreasing for 12v battery
        percent = float(100*tmp2/345600)#total wattage for fully discharge: 345600=12*8*3600
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Battery Percent:%.2f %%"
        % (hina260.current, hina260.voltage, hina260.power, consume, percent)) #Display discharging parameter on screen every second
        print("\n")#new line
        with open("log_12_d.csv","a") as record:  #save discharge data in a csv
            record.write("{0:0.2f}".format(hina260.current)+","+"{0:0.2f}".format(hina260.voltage)+","+"{0:0.2f}".format(hina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
    
    elif("c" in command):
        consume = consume + (hina260.power)/1000 
        tmp2 = tmp2 + (hina260.power/1000)#total power increasing for 12v battery
        percent = float(100*tmp2/345600)#total wattage for fully charge: 345600=12*8*3600
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Battery Percent:%.2f %%"
        % (hina260.current, hina260.voltage, hina260.power, consume, percent)) #Display charging parameter on screen every second
        print("\n")#new line
        
        with open("log_12_c.csv","a") as record:  #save discharge data in a csv
            record.write("{0:0.2f}".format(hina260.current)+","+"{0:0.2f}".format(hina260.voltage)+","+"{0:0.2f}".format(hina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
    

    with open('12.csv','w') as twelve_w: #change discharge level in the csv
        twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level

        
    time.sleep(1)
