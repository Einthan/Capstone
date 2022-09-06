import time#get timer library
import board#get rpi board library

#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
import adafruit_ina260#import sensor library
i2c = board.I2C()#set i2c pin for data input
cina260 = adafruit_ina260.INA260(i2c,0x41)#hook data input to this variable

charge = float(0)
tmp1 = float(0)#record car battery capacity
tmp2 = float(0)#record home battery capacity
percent1=float(0)#record car battery percent
percent2=float(0)#record home battery percent
oc_counter=int(0)#counter to set when car is charged to that level
charge_need=float(0)#to save how many power is needed to charge the battery to that level from zero charge
to_charge=float(0)#to save how many power is needed to charge the battery to that level from program estimated car battery level
car_vol=float(0)#to detect car battery level with reading the car voltage

battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car

while(float(battery)<10 or float(battery)>100):#out  of bound user input detection
    print("Invalid charge level, please re-enter again")
    battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car
    
charge_need = 39960*2*float(battery)/100 #set charge needed starting from 0 charge

with open('8dc.csv','r') as eight_r:#read home battery charged level from memory
    data1 = float(eight_r.read())#read to data2
    print("Car Wattage ",data1)
    tmp1=float(data1)#set tmp2 to it, as float
while charge_need < tmp1:#detect charge needed with self charge, for charging guard
    print("Car battery has higher percentage than you entered, rerun the program again")#let user re enter the charge level
    print("\n")
    print("current car battery level estimation :" , 100*tmp1/2/39960)#print charge estimation
    battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#re-enter
    charge_need = 39960*2*float(battery)/100 #claculate how many charge needed for charging to that percent from zero capacity
    time.sleep(1)#detect every second

print("current car battery level estimation :" , 100*tmp1/2/39960)#print charge estimation
to_charge= charge_need-tmp1#claculate how many charge needed for charging to that percent from current home capacity

while True:
    from datetime import datetime#get time module

    now = datetime.now()#set time now

    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second))#display time

    charge = charge + (cina260.power)/1000 #calculate power charging in W every second for whole time

    tmp1 = tmp1 + cina260.power/1000#charging for car
    percent1 = float(100*tmp1/39960/2) #percent of car battery

    if(tmp1>=charge_need):    #charge to that level counter
        oc_counter+=1   #increment every second it detected
        if(oc_counter>=30):    #30 seconds after going around that charge level, send complete massage
            print("BATTERY IS CHARGED TO THE DESIRED LEVEL, PLEASE DISCONNECT THE CHARGER ")

    with open("log_8_dccharge.csv","a") as record: #add discharging characterstic to this file
        record.write("{0:0.2f}".format(cina260.current)+","+"{0:0.2f}".format(cina260.voltage)+","+"{0:0.2f}".format(cina260.power)+","+"{0:0.2f}".format(percent1)+",")
        record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#time

    with open('8dc.csv','w') as eight_w:#update battery charge level
        eight_w.write("{0:0.2f}".format(tmp1))#write
        
    print(
    "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
    % (cina260.current, cina260.voltage, cina260.power, charge, percent1))#monitor two battery in real time
        
    time.sleep(1)#detect every second
