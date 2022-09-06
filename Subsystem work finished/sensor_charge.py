# This charging algorithm mainly ready for 12v home battery,
#it can monitor 3.7v battery percentage but does not self detect the data

#monitor either car or home, not both
#If no battery is connected, it output the last charged battery percentage
import time
import board

import adafruit_ina260  #import sensor library
#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
i2c = board.I2C()   #set i2c pin for data input
ina260 = adafruit_ina260.INA260(i2c)    #hock data input to this variable

charge = float(0)   #define charge level
tmp1 = float(0) #define charge level for 3.7v battery
tmp2 = float(0) #defined charge level for 12v battery
tmp3 = float(0) #define charge level for 8v battery

oc_counter=int(0)   #defined over cgharge counter alert

battery = input("Enter your batter type(Type 8 or 12 or 3.7): ")    #take input from users for 3.7v battery or 12 v

if "3.7" in battery: #open stored 3.7v charge level data, initial 60%
    print("3.7 v battery found")
    with open('3.7.csv','r') as three_r:    #open the pervious stroed 3.7 capacity data
        data = float(three_r.read())    #read data into float
    print("Wattage ",data)  #print how many charge left
    tmp1=float(data)    #set temporary charge level to tmp1

elif "12" in battery: #open stored 12v charge level data
    print("12 v battery found")
    with open('12.csv','r') as twelve_r:    #open the pervious stroed 12v capacity data
        data = float(twelve_r.read())   #read data into float
    print("Wattage ",data)  #print how many charge left
    tmp2=float(data)    #set temporary charge level to tmp2
elif "8" in battery: #open stored 3.7v charge level data, initial 60%
    print("8 v battery found")
    with open('8.csv','r') as eight_r:    #open the pervious stroed 8 capacity data
        data = float(eight_r.read())    #read data into float
    print("Wattage ",data)  #print how many charge left
    tmp3=float(data)    #set temporary charge level to tmp1
while True: #triigger when sensor is connected to the battery and reads data
    from datetime import datetime   #get tiem module

    now = datetime.now()    #get date, time now

    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second))   #print the date, time now

    charge = charge + (ina260.power)/1000 #calculate power charging in W every second for whole time

    if(tmp1 !=0):   #Monitor only 3.7 battery charging
        if(ina260.voltage>=4.1): #Overcharging protection high voltage
            oc_counter = oc_counter + 1 #increment every second
            if(oc_counter>=180):    #3 minutes for estimated fully charge for stop charging
                print("3.7 battery is fully charged, please disconnect the charger")   #output charge complete to user
                tmp1= 39960 #set to fully charged battery charge wattage,for 39960 w be the total power: 3.7v*3ah*3600s/h,connect in series does no increase the total amp hour
        tmp1 = tmp1 + ina260.power/1000     #calculate state of charging every second
        percent = float(100*tmp1/39960) #Calculate percentage every second
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, charge, percent))  #Display charging parameter on screen


        print("\n")#newline

        with open("log_3.7_charge.csv","a") as record: #add charging characterstic to this file
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#write in csv format
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#write date/time in the last column

        with open('3.7.csv','w') as three_w:#update battery charge level every second
            three_w.write("{0:0.2f}".format(tmp1))#write in this csv

    elif(tmp2 !=0): #monitor charging of the 12v home battery
        tmp2 = tmp2 + ina260.power/1000 #accumulate power input to the base battery data
        percent = float(100*tmp2/345600)#calculate charge percent,for 345600 w be the total power: 12v*8ah*3600s/h
        if(ina260.voltage>14.3):    #Over charge protection for 12v battery
            oc_counter+=1
            if(oc_counter>=180):    #3 minutes after close to over charge, send warning
                print("BATTERY IS AMOST FULLY CHARGED, PLEASE DISCONNECT THE CHARGER ")
                tmp2=345600;#set to fully charged measurment
        if((ina260.voltage>=13.4)&(percent<25)):#set to 25 percent if charging is too low
            tmp2=86400#25percent 
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, charge, percent))  #Display charging parameter on screen

        print("\n")#newline

        with open('12.csv','w') as twelve_w:    #update 12v battery data
            twelve_w.write("{0:0.2f}".format(tmp2))#write in csv

        with open("log_12_charge.csv","a") as record:#record charging data
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#record, current, voltage,power, percent
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record time in csv

    elif(tmp3 !=0):   #Monitor only 8 battery charging
        if(ina260.voltage>=8.2): #Overcharging protection high voltage
            oc_counter = oc_counter + 1 #increment every second
            if(oc_counter>=180):    #3 minutes for estimated fully charge for stop charging
                print("8 battery is fully charged, please disconnect the charger")   #output charge complete to user
                tmp3= 79920 #set to fully charged battery charge wattage,for 79920 w be the total power: 3.7v*2*3ah*3600s/h,connect in series does no increase the total amp hour
        tmp3 = tmp3 + ina260.power/1000     #calculate state of charging every second
        percent = float(100*tmp3/79920) #Calculate percentage every second
        print(
        "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Battery Percent:%.2f %%"
        % (ina260.current, ina260.voltage, ina260.power, charge, percent))  #Display charging parameter on screen


        print("\n")#newline


        with open("log_8_charge.csv","a") as record: #add charging characterstic to this file
            record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent)+",")#write in csv format
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#write date/time in the last column

        with open('8.csv','w') as three_w:#update battery charge level every second
            three_w.write("{0:0.2f}".format(tmp3))#write in this csv

    else:
        print("No battery is detected")    #if user type something else, print this



    time.sleep(1)   #rerun program every second until user stop it