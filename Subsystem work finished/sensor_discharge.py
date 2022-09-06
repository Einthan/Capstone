# This  discharging algorithm mainly ready for 12v home battery,
#it can monitor 3.7v battery percentage but does not self regulate the data

#either 12v or 3.7v
#If no battery is connected, it output the last charged battery percentage
import time #get timer library
import board    #get rpi board library

import adafruit_ina260#import sensor library
#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
i2c = board.I2C()#set i2c pin for data input
ina260 = adafruit_ina260.INA260(i2c)#hook data input to this variable

consume = float(0)  #define discharge total watt
tmp1 = float(0)#define charge level for 3.7v battery
tmp2 = float(0)#define charge level for 12v battery
tmp3 = float(0)#define charge level for 8v battery
guard = int(0)#define battery guard
battery = input("Enter your batter type (Type 3.7 or 12 or 8): ")#take input from users for 3.7v battery or 12 v

if "3.7" in battery: #open stored 3.7v charge level data
    print("3.7 v battery found")
    with open('3.7.csv','r') as three_r:#open the pervious stroed 3.7 capacity data
        data = float(three_r.read())#read data into float
    print("Wattage ",data)#print how many charge left
    tmp1=float(data)#set temporary charge level to tmp1

elif "12" in battery: #open stored 12v charge level data
    print("12 v battery found")
    with open('12.csv','r') as twelve_r: #open the pervious stroed 12 capacity data
        data = float(twelve_r.read()) #read data into float
    print("Wattage ",data)#print how many charge left
    tmp2=float(data)#set temporary charge level to tmp2
    
elif "8" in battery: #open stored 12v charge level data
    print("8 v battery found")
    with open('8.csv','r') as eight_r: #open the pervious stroed 12 capacity data
        data = float(eight_r.read()) #read data into float
    print("Wattage ",data)#print how many charge left
    tmp3=float(data)#set temporary charge level to tmp2

while True:#triigger when sensor is connected to the battery and reads data
    from datetime import datetime#get time module

    now = datetime.now()#get date, time now

    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)) #print the date, time now

    consume = consume + (ina260.power)/1000 #calculate power consumption in W every second

    if(tmp1 !=0):#Monitor 3.7 battery discharging
        tmp1 = tmp1 - (ina260.power/1000)#total power decreasing for 3.7v battery
        if((ina260.voltage<=3.2)&(ina260.voltage>3.1)):#over discharge protection parameter
            print("DANGER!!!BATTERY ABOUT TO DIE, STOP DISCHARGE IMMEDIATELY")#print out warning message
            if((tmp1>3996+800)&(guard==0)):#if battery level greater than 10% + 2%error of teh total charge
                tmp1=3996   #fix battery level to 10%
                guard=1
        percent = float(100*tmp1/39960) #was 24548.2, calculate every second

        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, consume, percent)) #Display charging parameter on screen every second


        print("\n")#new line
        with open("log_3.7.csv","a") as record: #add discharging characterstic to this file
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#write data in csv format
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#write date time in csv

        with open('3.7.csv','w') as three_w:#update battery discharge level for 3.7v battery
            three_w.write("{0:0.2f}".format(tmp1))#write in cvs

    elif(tmp2 !=0):#Monitor 12 battery discharging


        tmp2 = tmp2 - (ina260.power/1000)#total power decreasing for 12v battery
        percent = float(100*tmp2/345600)#total wattage for fully discharge: 345600=12*8*3600

        if(ina260.voltage==13.0):#battery medium level checker from discharge behavior test
            if((percent > 45+2)&&(guard==0)):#fix percentage if needed, added error margine of 2 percent
                tmp2=155520 #correct the power left over to be 45% of the battery if errors are big
                guard=1
        if(ina260.voltage==12.97):#reset guard parameter at lower charge
            guard =0;
        if((ina260.voltage<=10.8)&(ina260.voltage>10.3)):#Low voltage zoon, over used the battery
            print("DANGER!!!BATTERY IS BELOW 10%, STOP DISCHARGING IMMEDIATELY")#send out warning
            if(guard==0):
                tmp2=17280 #correct the power left over to be 5% for over discharge prevention
                guard==1
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, consume, percent)) #Display charging parameter on screen every second


        print("\n")#new line
        with open('12.csv','w') as twelve_w: #change discharge level in the csv
            twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level


        with open("log_12.csv","a") as record:  #save discharge data in a csv
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
    elif(tmp3 !=0):#Monitor 8v battery discharging


        tmp3 = tmp3 - (ina260.power/1000)#total power decreasing for 12v battery
        percent = float(100*tmp3/79920)#total wattage for fully discharge: 345600=12*8*3600

        if(ina260.voltage==7.3):#battery medium level checker from discharge behavior test
            if((percent > 42)& (guard==0)):#fix percentage if needed
                tmp3=31168; #correct the power left over to be 40% of the battery if errors are big
                guard=1

        if((ina260.voltage<=7.0)&(ina260.voltage>6.9)):#Low voltage zoon, over used the battery
            print("DANGER!!!BATTERY IS BELOW 10%, STOP DISCHARGING IMMEDIATELY")#send out warning
            tmp2=7992; #correct the power left over to be 10% for over discharge prevention

        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, consume, percent)) #Display charging parameter on screen every second


        print("\n")#new line
        with open('8.csv','w') as twelve_w: #change discharge level in the csv
            twelve_w.write("{0:0.2f}".format(tmp3))#write data from saved pervious battery level


        with open("log_8.csv","a") as record:  #save discharge data in a csv
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date

    else:
        print("No battery is detected")    #if user type something else, print this

    time.sleep(1)#rerun program every second until user stop it