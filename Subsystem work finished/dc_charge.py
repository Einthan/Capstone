# This charging algorithm is ready for car charging home battery

#If no battery is connected, it output the last charged battery percentage
import time#get timer library
import board#get rpi board library

#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
import adafruit_ina260#import sensor library
i2c = board.I2C()#set i2c pin for data input
ina260 = adafruit_ina260.INA260(i2c)#hook data input to this variable

charge = float(0)
tmp1 = float(0)#record car battery capacity
tmp2 = float(0)#record home battery capacity
percent1=float(0)#record car battery percent
percent2=float(0)#record home battery percent
oc_counter=int(0)#counter to set when car is charged to that level
charge_need=float(0)#to save how many power is needed to charge the battery to that level from zero charge
to_charge=float(0)#to save how many power is needed to charge the battery to that level from program estimated car battery level
car_vol=float(0)#to detect car battery level with reading the car voltage


#Self detect charge level of car battery algorithm
while (car_vol<2):#set to 2v incase detect some electric noise voltage, loop if not detect what we want
    print("Connect vin- pin from sensor to + terminal of te car battery, it is for charge level detection. Do not connect charger yet")
    car_vol=ina260.voltage#sense voltage from lower end
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
        tmp1=39960*2*0.5#60percent
    if((car_vol<3.72*2)&(car_vol>3.62*2)):
        tmp1=39960*2*0.4#40percent
    if((car_vol>=3.55*2)&(car_vol<3.62*2)):
        tmp1=39960*2*0.3#30percent
    if((car_vol>=3.5*2)&(car_vol<3.55*2)):
        tmp1=39960*2*0.2#20percent
    if((car_vol>=3.4*2)&(car_vol<3.5*2)):
        tmp1=39960*2*0.15#15percent
    if((car_vol>=3.3*2)&(car_vol<3.4*2)):
        tmp1=39960*2*0.1#10percent
    if((car_vol<3.3*2)&(car_vol>=3.2*2)):
        tmp1=39960*2*0.01#1percent,set to protect battery from over discharging
    elif((car_vol<3.2*2)):
        tmp1=0#1percent,set to protect battery from over discharging
        print("Car battery is dead or no battery detected :")#if the voltage is too low, print this
    print("Car battery level :",tmp1/39960/2*100,"%")#print how many percent the car battery estimate to havve
    time.sleep(1)#detect every second


battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car

while(float(battery)<10 or float(battery)>100):#out  of bound user input detection
    print("Invalid charge level, please re-enter again")
    battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car



with open('12.csv','r') as twelve_r:#read home battery charged level from memory
    data2 = float(twelve_r.read())#read to data2
    print("Home Battery Wattage ",data2)
    tmp2=float(data2)#set tmp2 to it, as float

charge_need = 39960*2*float(battery)/100 #set charge needed starting from 0 charge

while charge_need < tmp1:#detect charge needed with self charge, for charging guard
    print("Car battery has higher percentage then you entered, rerun the program again")#let user re enter the charge level
    print("\n")
    print("current car battery level estimation :" , 100*tmp1/2/39960)#print charge estimation
    battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#re-enter
    charge_need = 39960*2*float(battery)/100 #claculate how many charge needed for charging to that percent from zero capacity
    time.sleep(1)#detect every second

to_charge= charge_need-tmp1#claculate how many charge needed for charging to that percent from current home capacity

while((to_charge/0.6)>tmp2*0.1): #protect home battery from over discharge by not charging it, taken into account of worst case of converter efficiency
    print("Currently home battery does not support these much of charge, please exit the program")
    print("\n")
    print("current home battery level estimation" + ":" + 100*tmp2/345600 + "W")

    time.sleep(1)#print every second

print("Ready to charge. Connect v+ of charger to vin+ of sensor and vin- to + terminal of the car battery for charge monitoring")#print ready message
print("You can connect charger now") #print ready message
print("Message will disappear in 10 seconds")#print ready message
time.sleep(10)#10s later, start charging record


while True:
    from datetime import datetime#get time module

    now = datetime.now()#set time now

    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second))#display time

    charge = charge + (ina260.power)/1000 #calculate power charging in W every second for whole time

    tmp1 = tmp1 + ina260.power/1000#charging for car
    percent1 = float(100*tmp1/39960/2) #percent of car battery

    if(tmp1>=charge_need):    #charge to that level counter
        oc_counter+=1   #increment every second it detected
        if(oc_counter>=30):    #30 seconds after going around that charge level, send complete massage
            print("BATTERY IS CHARGED TO THE DESIRED LEVEL, PLEASE DISCONNECT THE CHARGER ")

    with open("log_8_dccharge.csv","a") as record: #add discharging characterstic to this file
        record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent1)+",")
        record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#time

    with open('8dc.csv','w') as three_w:#update battery charge level
        three_w.write("{0:0.2f}".format(tmp1))#write

        tmp2 = tmp2 -ina260.power/(0.6*1000) #efficiency of the dc-dc converter has average of 60% at 13-12v output, total power out from upper side is Pin=Pout/efficiency

        percent2 = float(100*tmp2/345600)#12v percentage left

    with open('12.csv','w') as twelve_w:#update 12v battery
        twelve_w.write("{0:0.2f}".format(tmp2))

    with open("log_12.csv","a") as record:#add 12v battery usage data
        record.write("{0:0.2f}".format(ina260.current)+","+"{0:0.2f}".format(ina260.voltage)+","+"{0:0.2f}".format(ina260.power)+","+"{0:0.2f}".format(percent2)+",")
        record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")

    print(
    "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %% Home Battery Percent:%.2f %%"
    % (ina260.current, ina260.voltage, ina260.power, charge, percent1, percent2))#monitor two battery in real time


    print("\n")


    time.sleep(1)#detect every second