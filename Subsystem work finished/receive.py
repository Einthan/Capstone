import imaplib
import time

import sys

#remember to create the local csv in the same code folder
while True:#infinity read latest email code
    with open('time.csv','r') as time_r:#make a local csv file, put a 0 in it
            t = float(time_r.read())#read
            print("Last data ",t)
    prevData = t
    while (prevData==t):
        
        user = 'wura123d@gmail.com'
        password = 'miqysmuvuzacraik'
        imap_url = 'imap.gmail.com'
            
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
            
        # this is done to make SSL connection with GMAIL
        con = imaplib.IMAP4_SSL(imap_url)
            
        # logging the user in
        con.login(user, password)
            
        # calling function to check for email under this label
        con.select('Inbox')
            
        # fetching emails from this user "tu**h*****1@gmail.com"
        msgs = get_emails(search('FROM', 'yu1820930063@gmail.com', con))
            
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
                    
                        if (prevData !=float(data2[0])):
                                print(data2[0:indexend])#split the 5 number with comma
                                splitUp = data2[0:indexend].split(',')
                                c0 = splitUp[0]
                                c1 = splitUp[1]
                                c2 = splitUp[2]
                                c3 = splitUp[3]
                                c4 = splitUp[4]
                                with open('time.csv','w') as time_w:#update the unique number, in this case the first number
                                    time_w.write("{0:0.2f}".format(float(c0)))
                                    print("New data ",c0)
                                prevData=float(c0)
                                c0=int(c0)
                                c1=int(c1)
                                c2=int(c2)
                                c3=int(c3)
                                c4=int(c4)
                                
                                print("end reading")
                    except UnicodeEncodeError as e:
                        pass
    
    
    print("end round")