

import smtplib
import time
import board

import adafruit_ina260

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = '???' #change this to match your gmail account
GMAIL_PASSWORD = '???'  #change this to match your gmail app-password

i2c = board.I2C()
hina260 = adafruit_ina260.INA260(i2c,0x40) #First Sensor read from 0x40 address

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

battery= 65 #Set battery current level, will be set to a real data at later stage when the charging system is implemented
counter=10  #Delay sent for 10 second
sendTo = '???'#change to the email receiver
emailSubject = "Real time test"
while True:
    from datetime import datetime
   
    now = datetime.now()
    print("home system:")
    print ("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second))
    
    battery+= battery*0.0004 #test algroithm, will be change to the real one when the charging system is implemented
    print(
    "Current: %.2f mA Voltage: %.2f V Power:%.2f mW Charge level: %.2f %%"
    % (hina260.current, hina260.voltage, hina260.power, battery))  #display status locally
    
    print("\n")
    sender = Emailer()
    s=str("%s/%s/%s %s:%s:%s" % (now.month,now.day,now.year,now.hour,now.minute,now.second)+" Current: %.2f mA Voltage: %.2f V Power:%.2f mW Battery level:%.2f %%"
    % (hina260.current, hina260.voltage, hina260.power,battery))
    
    with open("test.csv","a") as record: #add discharging characterstic to this file
            record.write("{0:0.2f}".format(hina260.current)+","+"{0:0.2f}".format(hina260.voltage)+","+"{0:0.2f}".format(hina260.power)+","+"{0:0.2f}".format(battery)+",")#write data in csv format
            record.write(datetime.today().strftime('%Y-%m-%d'+"," '%H:%M:%S')+"\n") #write date time in csv

    if(counter<=10):
        counter+=1
    else:
        counter=0
        
        emailContent = s #set the string so the email can sent to data

        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        sender.sendmail(sendTo, emailSubject, emailContent)

    #file.close()
    time.sleep(1)
    



