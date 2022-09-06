import RPi.GPIO as GPIO
# allows us to incorporate delays to allow some time between opening and closing relays	
import time
import sys
# deal with GPIO numbers instead of board numbers
GPIO.setmode(GPIO.BOARD)

# initialize the pins used for the Raspberry Pi output signal to the relay
# Relay 1
GPIO.setup(11, GPIO.OUT)# output pin

# Relay 2
GPIO.setup(13, GPIO.OUT)# output pin

tc=85#simulate battery current stage of charge
s=90  #say we want to charge to 90%
ui=int(input("Which source to use, type 1 for battery, 2 for wall outlet: ")
)
"""
try/finally code block to run all code in the try block and clean up all the GPIO pins when ctrl+C is entered so that there's no interference with future programs 
"""
try:
# loop indefinite amount of times until code is interrupted
    while True:
    # when the signal is low, relay is on and its LED light is on
        if((ui==1)&(tc<=s)):
            # turn on relay 1
            GPIO.output(11, GPIO.HIGH)
            tc+=1
            print('Battery is ON')
            time.sleep(1)
            
        
        elif((ui==2)&(tc<=s)):
            # turn on relay 2
            GPIO.output(13, GPIO.HIGH)
            tc+=1
            print('Ac is ON')
            time.sleep(1)
        
        
        else:
            # turn it off
            GPIO.output(11, GPIO.LOW)
            print('Battery is OFF')
            

            # turn off relay 2
            GPIO.output(13, GPIO.LOW)
            print('AC is OFF')
            
            sys.exit('Detection system shut down')
            

finally:
    print("exiting")
    GPIO.cleanup()
