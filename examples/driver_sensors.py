#toy example showing the use of live streaming data from a Comma Panda when connected to a car
#shows turn signal, brake, gear, and steering -- all save sensors to play with in the driver's seat
import liveTools as lt

p = lt.connectPanda()

turnSignal=''
brake = 0
gear = ''
steer = 0

try:
    while True:
        if p != 0:
            nturnSignal,nbrake, ngear, nsteer = lt.liveTest(p)
            if nturnSignal != None:
                turnSignal = nturnSignal
            if nbrake != None:
                brake = nbrake
            if ngear != None:
                gear = ngear
            if nsteer != None:
                steer = nsteer
            print('Turn Signal: ', turnSignal,'Brake Proportion: ', brake,'Gear: ',gear,'Steering: ',steer, end='\r')
        else:
            print('No device connected.')
            break
except KeyboardInterrupt:
    print('\n Session Ended')
