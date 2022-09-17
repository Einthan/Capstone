import time #get timer library
import board   #set rpi board mode using circuit python
import sys#to make the code stop under curtain command
import RPi.GPIO as GPIO#to guard GPIO
import digitalio #to control gpio uder board mode
import adafruit_ina260#import sensor library
import smtplib#email data library

#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
#setting switch control on raspberry GPIO 17 as home battery charging switch
home = digitalio.DigitalInOut(board.D17)
home.direction = digitalio.Direction.OUTPUT
#setting switch control on raspberry GPIO 27 as wall outlet charging switch
grid = digitalio.DigitalInOut(board.D27)
grid.direction = digitalio.Direction.OUTPUT

i2c = board.I2C()#set i2c pin for data input
hina260 = adafruit_ina260.INA260(i2c,0x40)#hook home data input to this variable
cina260 = adafruit_ina260.INA260(i2c,0x41)#hook car data input to this variable

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'wura123d@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'miqysmuvuzacraik'  #change this to match your gmail app-password
class Emailer:
    def sendmail(self, recipient, subject, content):

        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit
sendTo = 'emailfor404data@gmail.com'
tmp1 = float(0)#record car battery capacity
tmp2 = float(0)#define charge level for 12v battery
while True: #outer while loop to run the program again when it ended 
    consume = float(0)  #define discharge total watt
    
    charge = float(0)#charging accumulation value in mil-watt
    
    percent1=float(0)#record car battery percent
    percent2=float(0)#record home battery percent
    oc_counter=int(0)#counter to set when car is charged to that level
    charge_need=float(0)#to save how many power is needed to charge the battery to that level from zero charge
    to_charge=float(0)#to save how many power is needed to charge the battery to that level from program estimated car battery level
    car_vol=float(0)#to detect car battery level with reading the car voltage
    e_counter=int(0)# the time counter to update user data
    source=str()#to check what user want to use as the charging source
    command = input("If the home battery is charging by the solar pannel, type c; If using the home battery as source, type d :")
    if(command !='c') & (command !='d'):
        print("Your option is not valid, please try again.")
        command = input("If the home battery is charging by the solar pannel, type c; If using the home battery as source, type d :")
        
    with open('12.csv','r') as twelve_r: #open the pervious stroed 12 capacity data
        data = float(twelve_r.read()) #read data into float
        tmp2=float(data)#set temporary charge level to tmp2
    print("home battery is at: "+ str(100*tmp2/345600)+"%") #display how many percen left


    if(command == 'd'):#comsuming home battery to charge car
        with open('8dc.csv','r') as eight_r:#read home battery charged level from memory
            data1 = float(eight_r.read())#read to data2
            tmp1=float(data1)#set tmp1 to it, as float
        print("Current car battery level estimation :" , str(100*tmp1/2/39960) + "%")#print charge estimation
        battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car
        charge_need = 39960*2*float(battery)/100 #set charge needed of car starting from 0 charge
       
        while(float(battery)<10 or float(battery)>100 or charge_need < tmp1):#out  of bound user input detection
            print("Invalid charge level, please re-enter again")
            print("Current car battery level estimation :" , 100*tmp1/2/39960)#print charge estimation
            battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#ask user for how mnay they want to charge the car
            charge_need = 39960*2*float(battery)/100 #claculate how many charge needed for charging to that percent from zero capacity
        #maybe dont need
        while charge_need < tmp1:#detect charge needed with self charge, for charging guard
            battery = input("Enter how much percent you want to charge the car battery (Type integer between 10 - 100): ")#re-enter
            charge_need = 39960*2*float(battery)/100 #claculate how many charge needed for charging to that percent from zero capacity
            
        
        to_charge= charge_need-tmp1#claculate how many charge needed for charging to that percent from
        source=input("Choose which source to charge your car battery, using home battery type h, if using grid type g: ")
        if(source=='h')&(to_charge>tmp2*1.1): #To protect the home battery from overdischarging
            print("Home battery does not have the capacity to charge your car now, please switch the source or exit ")
            source=input("Choose which source to charge your car battery, using home battery type h, if using grid type g: ")

        elif(source !='h') & (source !='g'):
            print("No such source, try again")
            source=input("Choose which source to charge your car battery, using home battery type h, if using grid type g: ")
    try:        
        while True:#trigger when sensor is connected to the battery and reads data
            from datetime import datetime#get time module

            now = datetime.now()#get date, time now
            print("\n")
            print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)) #print the date, time now
            sender = Emailer()
            if('d' in command) & ('h' in source):
                home.value = True#turn on home battery as source
                
                consume = consume + (hina260.power)/1000 #calculate power consumption in W every second
                tmp2 = tmp2 - (hina260.power/1000)#total power decreasing for 12v battery
                percent = float(100*tmp2/345600)#total wattage for fully discharge: 345600=12*8*3600
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Home Battery Percent:%.2f %%"
                % (hina260.current, hina260.voltage, hina260.power, consume, percent)) #Display discharging parameter on screen every second

                with open("log_12_d.csv","a") as record:  #save discharge data in a csv
                    record.write("{0:0.2f}".format(hina260.current)+","+"{0:0.2f}".format(hina260.voltage)+","+"{0:0.2f}".format(hina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
                    record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
                with open('12.csv','w') as twelve_w: #change discharge level in the csv
                    twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level
                    
                charge = charge + (cina260.power)/1000 #calculate power charging in W every second for whole time
                tmp1 = tmp1 + cina260.power/1000#charging for car
                percent1 = float(100*tmp1/39960/2) #percent of car battery

                

                with open("log_8_dccharge.csv","a") as record: #add discharging characterstic to this file
                    record.write("{0:0.2f}".format(cina260.current)+","+"{0:0.2f}".format(cina260.voltage)+","+"{0:0.2f}".format(cina260.power)+","+"{0:0.2f}".format(percent1)+",")
                    record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#time

                with open('8dc.csv','w') as eight_w:#update battery charge level
                    eight_w.write("{0:0.2f}".format(tmp1))#write
                        
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, charge, percent1))#monitor
                if(tmp1>=charge_need):    #charge to that level counter
                    oc_counter+=1   #increment every second it detected
                    if(oc_counter>=20):    #20 seconds after going around that charge level, send complete massage
                        print("BATTERY IS CHARGED TO THE DESIRED LEVEL, HOME BATTERY SWITCH AUTO TURN OFF ")
                        home.value = False#turn off battery source
                        break
                
                s=str("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+"\n"+"Home Battery: "+"Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Home Battery Percent:%.2f %%"
                % (hina260.current, hina260.voltage, hina260.power, consume, percent)+"\n"+"Car battery:"+"Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, charge, percent1))
                if(e_counter>9):#send email at 10s about both battery and time
                    e_counter=0
                    emailSubject = "home_charge_car"
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                e_counter+=1
            elif('g' in source):
                grid.value = True#use wall outlet to charge
                charge = charge + (cina260.power)/1000 #calculate power charging in W every second for whole time
                tmp1 = tmp1 + cina260.power/1000#charging for car
                percent1 = float(100*tmp1/39960/2) #percent of car battery

                
                        
                with open("log_8_dccharge.csv","a") as record: #add discharging characterstic to this file
                    record.write("{0:0.2f}".format(cina260.current)+","+"{0:0.2f}".format(cina260.voltage)+","+"{0:0.2f}".format(cina260.power)+","+"{0:0.2f}".format(percent1)+",")
                    record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#time

                with open('8dc.csv','w') as eight_w:#update battery charge level
                    eight_w.write("{0:0.2f}".format(tmp1))#write
                        
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, charge, percent1))#monitor two battery 
                s=str("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+"\n"+"Car battery:"+"Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, charge, percent1))
                
                if(tmp1>=charge_need):    #charge to that level counter
                    oc_counter+=1   #increment every second it detected
                    if(oc_counter>=20):    #20 seconds after going around that charge level, send complete massage
                        print("BATTERY IS CHARGED TO THE DESIRED LEVEL, WALL OUTLET SWITCH AUTO TURN OFF ")
                        grid.value = False#turn off wall outlet source
                        break
                    
                if(e_counter>9):#send email about car battery status
                    e_counter=0
                    emailSubject = "grid_charge_car"            
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                e_counter+=1
            
            elif("c" in command):
                consume = consume + (hina260.power)/1000 
                tmp2 = tmp2 + (hina260.power/1000)#total power increasing for 12v battery
                
                percent = float(100*tmp2/345600)#total wattage for fully charge: 345600=12*8*3600
                
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Home Battery Percent:%.2f %%"
                % (hina260.current, hina260.voltage, hina260.power, consume, percent)) #Display charging parameter on screen every second
                print("\n")#new line
                
                with open("log_12_c.csv","a") as record:  #save discharge data in a csv
                    record.write("{0:0.2f}".format(hina260.current)+","+"{0:0.2f}".format(hina260.voltage)+","+"{0:0.2f}".format(hina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
                    record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
            
                with open('12.csv','w') as twelve_w: #change discharge level in the csv
                    twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level
                
                if(hina260.voltage>=14.3):
                    print("Home battery is fully charged, sensing auto cut off")
                    break
                s=str("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+"\n"+"Home battery:"+"Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Home Battery Percent:%.2f %%"
                % (hina260.current, hina260.voltage, hina260.power, consume, percent))
                if(e_counter>9):
                    e_counter=0
                    emailSubject = "home_charge"
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                e_counter+=1
             
            time.sleep(1)
    except KeyboardInterrupt:
        print("The end")
        home.value = False
        grid.value=False
        if(tmp1!=0) &(tmp2!=0):#incase unexpected stop without writing the data to local csv
            with open('8dc.csv','w') as eight_w:#incase the program is stopped while writing
                        eight_w.write("{0:0.2f}".format(tmp1))#write
            
            with open('12.csv','w') as twelve_w: #change discharge level in the csv
                        twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level
        
    finally:
        print("Thank you for using\n")
        home.value = False
        grid.value=False

