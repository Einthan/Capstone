import imaplib#read email library
import time #get timer library
import board   #set rpi board mode using circuit python
import sys#to make the code stop under curtain command
import RPi.GPIO as GPIO#to guard GPIO
import digitalio #to control gpio uder board mode
import adafruit_ina260#import sensor library
import smtplib#write email data library

#ALl SENSOR CURRENT READ IN mA, VOLTAGE IN V, POWER IN mW
#setting switch control on raspberry GPIO 17 as home battery charging switch
home = digitalio.DigitalInOut(board.D17)
home.direction = digitalio.Direction.OUTPUT
#setting switch control on raspberry GPIO 27 as wall outlet charging switch
grid = digitalio.DigitalInOut(board.D27)
grid.direction = digitalio.Direction.OUTPUT

i2c = board.I2C()#set i2c pin for data input
hcina260=adafruit_ina260.INA260(i2c,0x45)#hook home data input from solar charger to this varivable
hina260 = adafruit_ina260.INA260(i2c,0x40)#hook car sensing data output to this variable
cina260 = adafruit_ina260.INA260(i2c,0x41)#hook car data input to this variable


#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'monitor4404@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'sexrcyyrgyswszsa'  #change this to match your gmail app-password
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
sendTo1= 'emailfor404data2@gmail.com'

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

# Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data
            
    # Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
            
    return msgs
    
tot_consume_home=float(0)#set for total home battery used when finish charging
tot_consume_grid=float(0)#set for total gid used, will reset when finish charging
tot_htime=float(0)#set time spent on active charging with home battery
tot_gtime=float(0)#set time spent on active charging with grid
while True: #outer while loop to run the program again when it ended
    from datetime import datetime#get time module
    now = datetime.now()#get date, time now
    consume = float(0)  #define discharge total watt
    tmp2 = float(0)#define charge level for 12v battery
    charge = float(0)#charging accumulation value in mil-watt
    tmp1 = float(0)#record car battery capacity
    percent1=float(0)#record car battery percent
    percent2=float(0)#record home battery percent
    oc_counter=int(0)#counter to set when car is charged to that level
    charge_need=float(0)#to save how many power is needed to charge the battery to that level from zero charge
    to_charge=float(0)#to save how many power is needed to charge the battery to that level from program estimated car battery level
    car_vol=float(0)#to detect car battery level with reading the car voltage
    e_counter=int(0)# the time counter to update user data
    source=str()#to check what user want to use as the charging source
    time_count=0#time counter for home battery charging
    timer=0#timer for source changing every 30 mins?#change to 0
    try:
        with open('time.csv','r') as time_r:#see if old email is read
            t = float(time_r.read())#read
            print("Last data ",t)
    except:
        with open('time.csv','a') as time_r:#create new history file if not email is receive before
            time_r.write("{0:0.2f}".format(float(0)))
            print("new file now")
        with open('time.csv','r') as time_r:#read the history created data
            t = float(time_r.read())#read
            print("Last data ",t, "new tho")
    
    prevData = t
    while (prevData==t):
        
        user = 'monitor4404@gmail.com'
        password = 'sexrcyyrgyswszsa'
        imap_url = 'imap.gmail.com'
            
        
            
        # this is done to make SSL connection with GMAIL
        con = imaplib.IMAP4_SSL(imap_url)
            
        # logging the user in
        con.login(user, password)
            
        # calling function to check for email under this label
        con.select('Inbox')
            
        # fetching emails from this user "tu**h*****1@gmail.com"
        msgs = get_emails(search('FROM', 'emailfor404data2@gmail.com', con))#change to user address
            
        # Uncomment this to see what actually comes as data
        # print(msgs)  
        # Finding the required content from our msgs
        # User can make custom changes in this part to
        # fetch the required content he / she needs
            
        # printing them by the order they are displayed in your gmail

        for msg in msgs[-1:]:
            for sent in msg:
                if type(sent) is tuple:
            
                    # encoding set as utf-8
                    content = str(sent[1], 'utf-8')
                    data = str(content)
            
                    # Handling errors related to unicodenecode
                    try:
                        indexstart = data.find("ltr")
                        data2 = data[indexstart + 5: len(data)]
                        indexend = data2.find("</div>")
            
                        # printtng the required content which we need
                        # to extract from our email i.e our body
                        #print(data2[0: indexend])
                        #indexend-78:indexend
                        #print(prevData)
                        #print(data2[indexend-90:indexend])
                        splitUp = data2.split(',')
                        if (splitUp[len(splitUp)-4][-2]) == " ": 
                            c0 = splitUp[len(splitUp)-4][-1]
                        else:
                            c0 = splitUp[len(splitUp)-4][-2:]
                        if (prevData !=float(c0)):
                                
                                #splitUp = data2.split(',')
                                
                                #if (splitUp[len(splitUp)-4][-2]) == " ": 
                                    #c0 = splitUp[len(splitUp)-4][-1]
                                #else:
                                    #c0 = splitUp[len(splitUp)-4][-2:]
                                c1 = splitUp[len(splitUp)-3]
                                c2 = splitUp[len(splitUp)-2]
                                c3 = splitUp[len(splitUp)-1]
                                
                                with open('time.csv','w') as time_w:#
                                    time_w.write("{0:0.2f}".format(float(c0)))#write
                                    print("New data ",c0)
                                prevData=float(c0)
                                
                                print("end reading")
                                c1=int(c1)#command for how to use home battery, 1 for charging car, 2 for check car battery , others for choose home battery charging time
                                
                                c2=int(c2)#percent for battery to charge to, 10 to 100
                                c3=int(c3)#choose which souce to charge,1 for home battery, 2 for grid AC

                            
                    except UnicodeEncodeError as e:
                        pass
                    
    command = c1#take 1 or 2 or seconds less than a day
    if(command !=1) & (command !=2) & (command >86400):
        print("Your option is not valid, please try again.")
        continue
    
    with open('12.csv','r') as twelve_r: #open the pervious stroed 12 capacity data
        data = float(twelve_r.read()) #read data into float
        tmp2=float(data)#set temporary charge level to tmp2
    print("home battery is at: "+ str(100*tmp2/345600)+"%") #display how many percen left
    
    with open('8dc.csv','r') as eight_r: #open the pervious stroed 8v capacity data
        data = float(eight_r.read()) #read data into float
        tmp1=float(data)#set temporary charge level to tmp1
    print("car battery is at: "+ str(100*tmp1/39960/2)+"%") #display how many percen left in history if not auto sensing
    
    
    
    if(command == 2):
        while (car_vol<2.8*2):#set to 2v incase detect some electric noise voltage, loop if not detect what we want   
            print("Connect vin+ pin from sensor to + terminal of the car battery, connect common ground to the - terminal of the battery, connect -terminal of the sensor to the test resistor. ")
            car_vol=hina260.voltage#sense voltage from car battey detecton end
            if(car_vol>4.15*2):
                tmp1=39960*2#fully charged
            if((car_vol>=4.05*2)&(car_vol<=4.15*2)):
                tmp1=39960*2*0.95#95percent
            if((car_vol<4.05*2)&(car_vol>=4.0*2)):
                tmp1=39960*2*0.9#90percent
            if((car_vol<4.0*2)&(car_vol>=3.9*2)):
                tmp1=39960*2*0.8#80percent
            if((car_vol<3.9*2)&(car_vol>=3.8*2)):
                tmp1=39960*2*0.7#70percent
            if((car_vol<3.8*2)&(car_vol>=3.75*2)):
                tmp1=39960*2*0.6#60percent
            if((car_vol>=3.72*2)&(car_vol<3.75*2)):
                tmp1=39960*2*0.45#45percent
            if((car_vol<3.72*2)&(car_vol>=3.653*2)):
                tmp1=39960*2*0.4#40percent
            if((car_vol>=3.61*2)&(car_vol<3.653*2)):#fixed
                tmp1=39960*2*0.3#30percent
            if((car_vol>=3.55*2)&(car_vol<3.61*2)):
                tmp1=39960*2*0.2#20percent
            if((car_vol>=3.4*2)&(car_vol<3.55*2)):
                tmp1=39960*2*0.1#10percent
            if((car_vol<3.4*2)&(car_vol>=3.2*2)):
                tmp1=39960*2*0.01#1percent,set to protect battery from over discharging
            elif((car_vol<3.2*2)):
                tmp1=0#1percent,set to protect battery from over discharging
                print("Car battery is dead or no battery detected ")#if the voltage is too low, print this
            print("Battery voltage: ",car_vol, " Battery current: ",hina260.current)
            print("Car battery level :",tmp1/39960/2*100,"%")#print how many percent the car battery estimate to have
            time.sleep(1)
        with open('8dc.csv','w') as eight_w:#update battery charge level
            eight_w.write("{0:0.2f}".format(tmp1))#write
        s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,0,0,0,0))
        #send detected battery status to users phone
        sender=Emailer()
        emailSubject = "reading_test"
        emailContent = s
        sender.sendmail(sendTo, emailSubject, emailContent)
        continue

    if(command == 1):#comsuming home battery to charge car, mode 2 for using home battery as source
        with open('8dc.csv','r') as eight_r:#read home battery charged level from memory
            data1 = float(eight_r.read())#read to data2
            tmp1=float(data1)#set tmp1 to it, as float
        print("Current car battery level estimation :" , str(100*tmp1/2/39960) + "%")#print charge estimation
        battery = c2 #command from user input,take 10 to 100

        charge_need = 39960*2*float(battery)/100 #set charge needed of car starting from 0 charge
        print(charge_need)
        if(float(battery)<10 or float(battery)>100 or charge_need < tmp1):#out  of bound user input detection
            print("Invalid charge level, please re-enter again")
            print("Current car battery level estimation :" , 100*tmp1/2/39960)#print charge estimation
            continue#ask user for how many they want to charge the car
             #claculate how many charge needed for charging to that percent from zero capacity         
        
        to_charge= charge_need-tmp1#claculate how many charge needed for charging to that percent from
        print("to_charge",to_charge,"tmp1 ",tmp1)
        source=c3#option 1 for using home as source, option 2 for using grid
        if(source==1)&(to_charge>tmp2*1.2): #To protect the home battery from overdischarging
            print("Home battery does not have the capacity to charge your car now, swtich to use grid ")
            source==2

        elif(source !=1) & (source !=2):
            print("No such source, try again")
            break
    ###################################
    try:        
        while True:#trigger when sensor is connected to the battery and reads data
            from datetime import datetime#get time module
            now = datetime.now()#get date, time now
            print("\n")
            print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)) #print the date, time now
            sender = Emailer()
            if(command==1) & (source==1):#charge car battery using home battery as source
                home.value = True#turn on home battery as source
                ###need to adjust home comsume after charger being tested, will be c.power/efficiency
                #from test the efficiency is 95%
                timer+=1 #timer for 30 mintues charging then check rate
                consume = consume + (cina260.power)/0.95/1000 #calculate power consumption in W every second
                tmp2 = tmp2 - (cina260.power/0.95/1000)#total power decreasing for 12v battery
                percent = float(100*tmp2/345600)#total wattage for fully discharge: 345600=12*8*3600
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Home Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, consume, percent)) #Display discharging parameter on screen every second


                with open('12.csv','w') as twelve_w: #change discharge level in the csv
                    twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level
                    
                charge = charge + (cina260.power)/1000 #calculate power charging in W every second for whole time
                tmp1 = tmp1 + cina260.power/1000#charging for car
                percent1 = float(100*tmp1/39960/2) #percent of car battery
                if(tmp1>=39960*2):    #fully charged 
                    tmp1=39960*2
                #maybe don't need estimation
                
                #if(cina260.power>10):
                    #speed = to_charge / cina260.power * 1000 /60 #estimate charging time for every second, in minutes
                    #speed=1440.00
                    
                    #to_charge = to_charge - cina260.power/1000
                    #print(to_charge)
                #elif(cina260.power==0):
                    #speed =1440.00#upper limit of 1 day in minutes, means system is not charging
                
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
                    tmp1=int(c2)*39960*2
                    if(oc_counter>=2):    #2 seconds after going around that charge level, send complete massage
                        print("BATTERY IS CHARGED TO THE DESIRED LEVEL, HOME BATTERY SWITCH AUTO TURN OFF ")
                        home.value = False#turn off battery source
                        kwat=consume/1000
                        #tot_consume_home+=kwat#update total charged
                        #tot_htime+=timer+oc_counter
                        s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,cina260.power,0,kwat,1))
                        #s=str("Total power used by home:%.2f KW Total power used by grid:%.2f KW Total time of charging with home battery:%.2f s Total time of charging with grid:%.2f s" %(tot_consume_home,tot_consume_grid, tot_htime,tot_gtime))#send kilowatt used for the grid charging
                        #The format:home%,car%,power in solar,home to car power, grid to car power, home comsume every 30mins, finish charging signal
                        emailSubject = "reading_test"            
                        emailContent = s
                        sender.sendmail(sendTo, emailSubject, emailContent)
                        #tot_consume_home=0
                        #tot_consume_grid=0
                        #tot_htime=0
                        #tot_gtime=0
                        break
                
                elif(timer>=280):#change to 1800
                    print("5 minutes charge complete by using home battery as source.")
                    home.value = False#turn off battery source
                    kwat=consume/1000
                    #tot_consume_home+=kwat#update total charged
                    #tot_htime+=1800
                    s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,0,0,kwat,0))#send kilowatt used for the grid charging
                    emailSubject = "reading_test"            
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                    
                    s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f"%(kwat))#send power charged using home battery every 30 minutes to front end server
                    emailSubject = "Home_power_used"            
                    emailContent = s
                    sender.sendmail(sendTo1, emailSubject, emailContent)
                    
                    break
                    
                s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,cina260.power,0,0,0))
                
                
                if(e_counter>9):#send email at 10s about both battery and time
                    e_counter=0
                    emailSubject = "reading_test"
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                e_counter+=1
            elif(command==1)&(source==2):#using grid to charge car battery 
                grid.value = True#use wall outlet to charge
                timer+=1
                charge = charge + (cina260.power)/1000 #calculate power charging in W every second for whole time
                tmp1 = tmp1 + cina260.power/1000#charging for car
                percent1 = float(100*tmp1/39960/2) #percent of car battery
                if(tmp1>39960*2):#fully charged
                    tmp1=39960*2

                #if(cina260.power>10):
                    #speed = to_charge / cina260.power *1000/60#estimate charging time for every second, in minutes
                    #speed=1440.00
                    #print("speed",speed)
                    #to_charge = to_charge - cina260.power/1000
                    #print("tocharge",to_charge)
                #elif(cina260.power==0):
                    #speed =1440.00#upper limit of 1 day in minutes, means system is not charging
                        
                with open("log_8_dccharge.csv","a") as record: #add discharging characterstic to this file
                    record.write("{0:0.2f}".format(cina260.current)+","+"{0:0.2f}".format(cina260.voltage)+","+"{0:0.2f}".format(cina260.power)+","+"{0:0.2f}".format(percent1)+",")
                    record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#time

                with open('8dc.csv','w') as eight_w:#update battery charge level
                    eight_w.write("{0:0.2f}".format(tmp1))#write
                        
                print(
                "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %%"
                % (cina260.current, cina260.voltage, cina260.power, charge, percent1))#monitor two battery 
                
                
                if(tmp1>=charge_need):    #charge to that level counter
                    tmp1=int(c2)*39960*2
                    oc_counter+=1   #increment every second it detected
                    if(oc_counter>=2):    #20 seconds after going around that charge level, send complete massage
                        print("CAR BATTERY IS CHARGED TO THE DESIRED LEVEL, WALL OUTLET SWITCH AUTO TURN OFF ")
                        grid.value = False#turn off wall outlet source
                        kwat=charge/1000
                        #tot_consume_grid+=kwat
                        #tot_gtime+=timer+oc_counter
                        s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,0,cina260.power,0,1))
                        #s=str("Total power used by home:%.2f KW Total power used by grid:%.2f KW Total time of charging with home battery:%.2f s Total time of charging with grid:%.2f s" %(tot_consume_home,tot_consume_grid, tot_htime,tot_gtime))#send kilowatt used for the grid charging
                        emailSubject = "reading_test"               
                        emailContent = s
                        sender.sendmail(sendTo, emailSubject, emailContent)
                        #tot_consume_home=0
                        #tot_consume_grid=0
                        #tot_htime=0
                        #tot_gtime=0
                        break
                elif(timer>=280):#change to 1800
                    print("5 minutes charge complete by using grid as source.")
                    grid.value = False#turn off battery source
                    #tot_gtime+=1800
                    kwat=charge/1000
                    #tot_consume_grid+=kwat
                    s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,0,0,0,0))
                    emailSubject = "reading_test"            
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                    break  
                #s=str("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+"\n"+"Car battery:"+"Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power charged:%.2f W Car Battery Percent:%.2f %% Remain Time Estimate:%.2f minutes"
                #% (cina260.current, cina260.voltage, cina260.power, charge, percent1,speed))
                s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,tmp1/39960/2*100,0,0,cina260.power,0,0))
                if(e_counter>9):#send email about car battery status
                    e_counter=0
                    emailSubject = "reading_test"            
                    emailContent = s
                    sender.sendmail(sendTo, emailSubject, emailContent)
                e_counter+=1
            
            elif(command!=2):#call for home battery charging by solar pannel
                e_counter+=1
                time_count+=1
                if(time_count<command):
                    if(hcina260.current>0):
                        consume = consume + (hcina260.power)/1000 
                        tmp2 = tmp2 + (hcina260.power/1000)#total power increasing for 12v battery
                    elif(hcina260.current<=0):
                        tmp2 = tmp2 - (hcina260.power/1000)#total power increasing for 12v battery
                    if(tmp2>345600):
                        tmp2=345600#set to 100 percent
                    percent = float(100*tmp2/345600)#total wattage for fully charge: 345600=12*8*3600
                    
                    
                    print(
                    "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Power Used:%.2f W Home Battery Percent:%.2f %%"
                    % (hcina260.current, hcina260.voltage, hcina260.power, consume, percent)) #Display charging parameter on screen every second
                    print("\n")#new line
                    
                    with open("log_12_c.csv","a") as record:  #save discharge data in a csv
                        record.write("{0:0.2f}".format(hcina260.current)+","+"{0:0.2f}".format(hcina260.voltage)+","+"{0:0.2f}".format(hcina260.power)+","+"{0:0.2f}".format(percent)+",")#record current, voltage,power, percent
                        record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n")#record date
                
                    with open('12.csv','w') as twelve_w: #change discharge level in the csv
                        twelve_w.write("{0:0.2f}".format(tmp2))#write data from saved pervious battery level
                    
                    if(hina260.voltage>=14.4):
                        print("Home battery is fully charged, sensing auto cut off")
                        break
                    s=str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,0,hcina260.power,0,0,0,0))
                    if(e_counter>9):
                        e_counter=0
                        emailSubject = "reading_test"
                        emailContent = s
                        sender.sendmail(sendTo, emailSubject, emailContent)                                 
                else:
                    print("Home battery stopped charging because of no more solar power!")
                    emailSubject = "reading_test"
                    emailContent =str("%s/%s/%s,%s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+","+"%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"%(100*tmp2/345600,0,120,0,0,0,0))
                    sender.sendmail(sendTo, emailSubject, emailContent) 
                    time_count=0
                    break
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






