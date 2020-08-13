import sys
sys.path.append('~/anaconda3/lib/python3.7/site-packages/panda/')
from panda import Panda
import binascii
import bitstring
import time
import datetime
#import serial
import csv
import cantools
import pandas as pd
import numpy as np
import simpleaudio as sa
import matplotlib.pyplot as plt
import liveTools as lt
import osascript
import keyboard
import random
import threading

startTime = time.time() #reference start time
validTime = time.time()
counter = 0
# osascript.osascript("set volume output volume " + volume)
def sound(f, length, volume = 40):
    osascript.osascript("set volume output volume " + str(volume))

    frequency = f  # Our played note will be 440 Hz
    fs = 44100  # 44100 samples per second
    seconds = length  # Note duration of 3 seconds

    # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
    t = np.linspace(0, seconds, int(seconds * fs), False)

    # Generate a 440 Hz sine wave
    note = np.sin(frequency * t * 2 * np.pi)

    # Ensure that highest value is in 16-bit range
    audio = note * (2**15 - 1) / np.max(np.abs(note))
    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()
    return audio
#load dbc file
db2 = lt.database('RAV4.dbc')
p = lt.connectPanda() #create panda object
df = 0.04
leader = lt.KF_Object([5,0],0, 0, df, 1,1,1)
reportTime = time.time()
#log data for analysis and playback later
    #update this so it uses libpanda
    #use/create a separate script that calls libpanda?
fileTime = int(time.time())
fileName = str(fileTime) + '_can_data.csv'
date,dString = lt.dateString(fileTime)
rf_PANDA = open(dString + '_can_data.csv', 'a')
print('Writing: '+dString)
csvwriter_PANDA = csv.writer(rf_PANDA)
csvwriter_PANDA.writerow(['Time','Bus', 'MessageID', 'MessageLength', 'Message'])

centerHz = 500
widthHz = 100
d = 0.25 #duration of beeps
vmax = 100 #maximum volume
slower = sound(centerHz-widthHz,d,vmax)
slow = sound(centerHz-widthHz,d,50)
fast = sound((centerHz+widthHz),d,50)
faster = sound((centerHz+widthHz),d,vmax)
lastBeep = time.time()
start = time.time()

def printit():
    t = threading.Timer(0.5, printit)
    t.start()
    # print(time.time())
    if th > 2.1:
        #if th > 2.2:
        play_obj = sa.play_buffer(faster,1,2,44100) #two higher beeps indicating speed up
    if th < 2.1 and th > 2.05:
        play_obj = sa.play_buffer(fast,1,2,44100)
    if th < 1.9 and th != -1:
        # if th < 1.8:
        play_obj = sa.play_buffer(slower,1,2,44100)
    if th > 1.9 and th < 1.95:
        play_obj = sa.play_buffer(slow,1,2,44100)

    def cancel():
        t.cancel()
    #make something for a good sound

    # end = time.time()
    # print('Elapsed: ',end-start)
    # start = time.time()
  #     # play_obj.wait_done()
  #     play_obj.stop()
  # print ("Hello, World!")


leadDist = 20
lead869 = 0
velocity = 40
vArray = []
aArray = []
leadArray = []
thArray = []
relvArray = []
thTime = []
twos = []
th = 3.14159
myrelv = 3
relv = -50
accel = -50
leadPosition=[3,0]

# for i in range(10):
#     hz = 150 + 7 * 10*i
#     print(i)
#     volume = abs(0.5*i - 50)
#     sound(hz,.02,volume)

#create plotting df
try:
    t = threading.Timer(0.5, printit)
    # threading.Timer(0.333, printit).start()
    # t = threading.Timer(0.5, printit,[th])
    t.start()
    while True:

        if time.time() >= reportTime:
            now = time.time()
            # if now > reportTime:
            reportTime = time.time()+df
            counter += 1
            # print(counter)
            leadArray.append(leader.get_coords()[1]) #KF of clustered radar measurement
            vArray.append(velocity/3.6)#most recent velocity measurement converted to m/s
            aArray.append(accel)
            relvArray.append(myrelv) #do NOT convert to kph
            if velocity > 0 and (now-validTime < 2):
                th = (leader.get_coords()[1])/(velocity/3.6) #distance divided by meters per second
            else:
                th = -1
            thArray.append(th)
            thTime.append(now)
            # twos.append(2)

        if p != 0:
            leader.predict()
            # print(leader.get_x(),leader.get_coords())
            can_recv = p.can_recv()

            for address, _, dat, src  in can_recv:
                currTime = time.time()
                csvwriter_PANDA.writerow(([currTime, str(src), str((address)), len(dat), str(binascii.hexlify(dat).decode('utf-8'))]))

                if address == 869:
                    print('something')
                    temp = list(db2.decode_message(address,dat).values())[6]
                    if temp < 252:
                        lead869 = temp
                        print(lead869)
                if address == 552:
                    # print(dat)
                    dat = bytes(dat).hex().ljust(16,'0')
                    accel = list(db2.decode_message(address,bytes.fromhex(dat)).values())[0]
                if address == 180:
                    velocity = list(db2.decode_message(address,dat).values())[1]


            leadPosition,relv,newVelocity,newAccel = lt.getClusteredRadar(p,writer = csvwriter_PANDA,recentLeadMeasurement = leadDist,velNaccel= True) #0.03 second timeout

        #this controller operates under the assumption that there is a lead vehicle
            if relv != None:
                leadDist = leadPosition[1] #longitude
                myrelv = relv
                validTime = time.time() #most recent valid measurement from radar
            if newVelocity != None:
                velocity = newVelocity
            if newAccel != None:
                accel = newAccel
            # if (lt.getVelocity(can_recv) != None): #this value is found faster above in the for loop
            #     velocity = lt.getVelocity(can_recv)


                # print('No valid time headway. Velocity is 0 or lead dist timed out.')
        else: #for when there is not a panda device connected
            leadDist = leadDist + (random.random()*10 - 5)
            th = leadDist/(velocity/3.6)
            while (th < 1.5) or (th > 2.5):
                leadDist = leadDist + (random.random()*10 - 5)
                th = leadDist/(velocity/3.6)
            thArray.append(th)
            thTime.append(time.time())
            twos.append(2)
            newVelocity = 40
            velocity = newVelocity
            relv = 1


        #update KF
        if relv != None: #if there is a measurement
            leader.update(leadPosition)


            # print('No Velocity')
        print('Lead 869: ',lead869,'Lead Dist: ', round(leadDist,3),'KF Dist: ',round(leader.get_coords()[1],3), end = '\r')

        # reportTime = time.time()+df
except KeyboardInterrupt:
    #save a file of TH, velocity, lead_dist prediction
    leadingVel = vArray.copy()


    for i in range(len(vArray)):
        leadingVel[i] = vArray[i]+relvArray[i]
    if p != 0:
        d = {'Timestamp': thTime, 'Follower Velocity':vArray,'Leader Velocity':leadingVel, 'Space Gap': leadArray,'Follower Acceleration': aArray,'Time Headway': thArray}
        pd.DataFrame(data= d).to_csv(dString + '_leadMeasurement.csv')
        d2 = {'Timestamp': thTime, 'Follower Velocity':vArray,'Relv':relvArray,'Space Gap': leadArray}
        pd.DataFrame(data= d2).to_csv(dString + '_velocityCheck.csv')

    plt.subplot(211)
    axes = plt.gca()
    axes.set_xlim([0,50])
    axes.set_ylim([0,100])
    plt.xlabel('Speed (m/s)')
    plt.ylabel('Lead Distance (m)')
    plt.title('Lead Distance vs. Speed')
    # v = vArray.copy()
    # for i in range(len(vArray)):
    #     v[i] = vArray[i] #convert to m/s to be compatible with the meters of lead distance
    plt.scatter(vArray,leadArray,c=thTime,cmap='viridis')
    plt.colorbar()
    y=np.linspace(0,100)
    x=np.linspace(0,50)
    plt.plot(x,y)

    plt.subplot(212)
    axes = plt.gca()
    axes.set_ylim([1,3])
    plt.xlabel('Time')
    plt.ylabel('Time Headway (s)')
    plt.title('Time Headway')
    plt.plot(thTime,thArray)

    twos = thArray.copy()
    for i in range(len(vArray)):
        twos[i] = 2

    plt.plot(thTime,twos)
    plt.tight_layout()
    plt.draw()
    # plt.pause(5)
    plt.savefig(str(fileTime)+'.png')


    print('rate of data recorded: ',counter/(thTime[-1]-thTime[0]))

    print("Fin.")
    t.join()
