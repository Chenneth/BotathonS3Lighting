import ctypes

import neopixel
import board
import time
import multiprocessing
import configparser
import atexit

filepath = "/home/pi/Documents/led.cfg"
config = configparser.ConfigParser()
config.read(filepath)
# default values for config if it can't find the cfg file
config['DEFAULT'] = {
    "StartCountdown": "1",
    "YellowSwitch": "1",
    "AutoTerm": "1",
    "IdleLights": "0",
    "StartTime": "180",
    "LowTime": "30",
    "SDTime": "90",
    "Countdown": "FFFFFF",
    "TimerNormal": "00FF00",
    "LowTime": "00FCFC",
    "GoalScored": "0000FF",
    "TimeUp": "FF0000",
    "IdleOne": "FFFFFF",
    "IdleTwo": "00FF00",
    "SuddenDeath":"FF0000",
    "LEDCount": "300"
}

# color configs
temp = config.get("COLORS", "Countdown")
COLOR_COUNTDOWN = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "TimerNormal")
COLOR_TIMER = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "LowTime")
COLOR_LOWTIME = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "GoalScored")
COLOR_GOALSCORED = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "TimeUp")
COLOR_TIMEUP = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "IdleOne")
COLOR_IDLEONE = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "IdleTwo")
COLOR_IDLETWO = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "SuddenDeath")
COLOR_SD = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

# behavior configs
STARTCOUNTDOWN = config.getboolean("BEHAVIOR", "StartCountdown")
YELLOWSWITCH = config.getint("BEHAVIOR", "YellowSwitch")
AUTOTERM = config.getint("BEHAVIOR", "AutoTerm")

# time configs
TIMERTIME = float(config.getint("TIMER", "StartTime"))
LOWTIME = config.getint("TIMER", "LowTime")
SDTIME = config.getint("TIMER", "SDTime")

pxlCnt = config.getint("MISC", "LEDCount")
pixels = neopixel.NeoPixel(board.D18, pxlCnt, auto_write=False)


#queue = multiprocessing.Queue()
pipeFront, pipeBack = multiprocessing.Pipe()
processes =[]

def StartDelayCount():
    # for x in range(100):
    #     pixels[x] = (255, 255, 255)
    # pixels.show()
    # time.sleep(1)
    # for x in range(101, 200):
    #     pixels[x] = (255, 255, 255)
    # pixels.show()
    # time.sleep(1)
    # for x in range(201, 300):
    #     pixels[x] = (255, 255, 255)
    # pixels.show()
    # time.sleep(1)
    for x in range(50):
        pixels[x]=(255,255,255)
        pixels[299-x]=(255,255,255)
    pixels.show()
    time.sleep(1)
    for x in range(50,100):
        pixels[x]=(255,255,255)
        pixels[299-x]=(255,255,255)
    pixels.show()
    time.sleep(1)
    for x in range(100,150):
        pixels[x]=(255,255,255)
        pixels[299-x]=(255,255,255)
    pixels.show()
    time.sleep(1)

def CopyCurrentColors():
    t=[pixels[0]]
    for x in range(pxlCnt):
        t.append(pixels[x])
    return t

def PasteCurrentColors(ColorsList):
    for x in range(pxlCnt):
        pixels[x]=ColorsList[x]
    pixels.show()

#todo: test this
def Goal():
    for x in range(pxlCnt):
        pixels[x]=COLOR_GOALSCORED
    pixels.brightness = 1.0
    pixels.show()
    time.sleep(.25)
    while pixels.brightness > 0.25:
        pixels.brightness-=0.05
        pixels.show()
        time.sleep(.025)
    pixels.brightness = 0.5
    pixels.show()
    while pixels.brightness<1.0:
        pixels.brightness+=0.05
        pixels.show()
        time.sleep(.025)
    pixels.brightness = 1.0
    time.sleep(3)
    while pixels.brightness > 0.05:
        pixels.brightness-=.05 #todo: dunno if it'll work with this (lowest i've tested is .25 increments
                                    #uhh basically, floats are funny and idk the gimmicks too much (had this problem with Unity too)
        pixels.show()
        time.sleep(.05)
    pixels.fill((0,0,0))
    pixels.brightness=1.0
    pixels.show()

#please give this pipeBack
def Countdown_Normal(pipe:multiprocessing.connection):
    pixels.fill(COLOR_TIMER)
    pixels.show()
    totalSeconds = TIMERTIME
    while totalSeconds > LOWTIME:  # 30 seconds is when it switches to yellow
        time.sleep(.1)
        totalSeconds -= .1
        if pipe.poll():
            msg = pipe.recv()
            print(msg)
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:])
                    print("Total time is now {}".format(totalSeconds))
                except:
                    print("Could not add the timer due to an error")
            else:
                if msg[:1]=="p":
                    print("Timer currently paused. Waiting.\n")
                    pixels.fill((47,47,79))
                    pixels.brightness = .3
                    pixels.show()
                elif msg[:1]=="g":
                    Goal()
                pipe.recv()
                pixels.fill((0,0,0))
                pixels.brightness = 1.0
                pixels.show()
                print("Resuming timer.")
                StartDelayCount()
                pixels.fill(COLOR_TIMER)
                pixels.show()
    start = time.time()
    offset=0.0
    for x in range(300):
        pixels[x] = (255, 255, 0)
        pixels.show()
        #checking this every loop because the lights don't update immediately (there's like a .5 second delay or something
        if pipe.poll():
            msg = pipe.recv()
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:]) - (time.time()-start - offset)
                    start = time.time()
                    offset = 0.0
                    print("Total time is now {}".format(totalSeconds))
                except:
                    print("Could not add the timer due to an error")
            else:
                tempList = CopyCurrentColors()
                if msg[:1]=="p":
                    pixels.fill((47,47,79))
                    pixels.brightness = .3
                    pixels.show()
                    print("Timer currently paused. Waiting.\n")
                elif msg[:1]=="g":
                    Goal()
                midStart = time.time()
                pipe.recv()
                offset+= time.time()-midStart
                print("Resuming timer.")
                StartDelayCount()
                PasteCurrentColors(tempList)
                pixels.show()
    totalSeconds -= float(time.time()-start - offset)

    while totalSeconds > -1:  # 30 seconds is when it switches to yellow
        time.sleep(1)
        totalSeconds -= 1
        if pipe.poll():
            msg = pipe.recv()
            #add time to the timer, i really don't feel like fixing the colors on this though, will ask seb
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:])
                    print("Total time is now {}".format(totalSeconds))
                except:
                    print("Could not add the timer due to an error")
            else:
                if msg[:1]=="p":
                    print("Timer currently paused. Waiting.\n")
                elif msg[:1]=="g":
                    Goal()
                pipe.recv()
                print("Resuming timer.")
                StartDelayCount()
                pixels.fill(COLOR_LOWTIME)

    pixels.fill(COLOR_TIMEUP)
    pixels.brightness = 0.5 #idk if you want me to have the brightness in the conf files too
    pixels.show()

    print("time's up")

def at_exit():
    global processes
    for process in processes:
        process.terminate()
    print("t")

#bad naming, I know
# this is the input process that's active for the duration of the timer
#please give this pipeFront, and CountdownTimer() pipeBack
def TimerInput(timerProcess:multiprocessing.Process,pipe:multiprocessing.connection):
    while timerProcess.is_alive():
        msg = input("Enter one of the following to edit the current timer:\n"
              "'p'\tPause the timer\n"
              "'a ##'\tAdd ## seconds to the timer\n"
              "'g'\tGoal was scored\n")
        pipe.send(msg)
        #sleep for 1.1 seconds to ensure that the other process receives the input instead of this one
        time.sleep(.2)
        if msg[:1]=='p' or msg[:1]=='g':
        #pause or goal scored
            secmsg = input("Press enter to continue...\n")
            pipe.send(secmsg)
        # i know this prevents rapid pausing and unpausing... but i don't have a good way to test this rn
        time.sleep(.2)

#todo: idk if this works (i imported
def SuddenDeath(queue:multiprocessing.Queue):
    a = (255, 0, 0)
    for x in range(300):
        pixels[x] = a
    startTime = time.time()

    goingDown = True
    brightness = 1.0
    pixels.brightness = 1.0
    pixels.show()

    while time.time() - startTime < 30:
        brightness = brightness - .025 if goingDown else brightness + .025
        if brightness < .2:
            goingDown = False
        elif brightness > .9:
            goingDown = True
        pixels.brightness = brightness
        pixels.show()
        time.sleep(.05)


if __name__=='__main__':
    atexit.register(at_exit)
    print("Current config values:\n")
    for sect in config.sections():
        print("Section [{}]:\n".format(str(sect)))
        for key,val in config.items(sect):
            print("{} = {}\m".format(key,val))
    if STARTCOUNTDOWN:
        print("This timer will have a 3 second countdown before starting.\n")
    else:
        print("Timer will start as soon as user inputs...maybe idk\n")
    #idk if terminal will allow it (because it didn't work with C++)
    input("Press 'enter' to start\n")
    continueProgram = True
    if AUTOTERM!=1:
        while continueProgram:
            if STARTCOUNTDOWN:
                StartDelayCount()
            #idk how to use Pools so I won't
            timerProcess = multiprocessing.Process(target=Countdown_Normal, args=[pipeBack])
            #inputProcess = multiprocessing.Process(target=TimerInput,args=[queue])
            processes.append(timerProcess)
            timerProcess.start()
            #inputProcess.start()
            #am i doing this right?
            #timerProcess.join()
            TimerInput(timerProcess,pipeFront)
            timerProcess.close()
            #inputProcess.terminate()
            processes.pop(0)
            #ask if sudden death
            MatchOver = input("Is the match over? Enter 0 to reset the timer, 1 to start sudden death, or 2 to turn off all LEDs and terminate the program.\nSudden death will start with a countdown.\n")
            if MatchOver==2: #terminate program
                continueProgram=False
            elif MatchOver==1: #sudden death
                timerProcess = multiprocessing.Process(target=SuddenDeath,args=[pipeBack])
                #yes i ctrlc ctrlv the next 9 lines, no i am not removing the comments
                #inputProcess = multiprocessing.Process(target=TimerInput, args=[queue])
                
                timerProcess.start()
                processes.append(timerProcess)
                TimerInput(timerProcess,pipeFront)
                #inputProcess.start()
                # am i doing this right?
                #timerProcess.join()

                timerProcess.close()
                processes.pop(0)
            else:
                continue #unnecessary but I'm really too tired to see anything rn


    
#todo: deinit the LEDs and stuff


# StartDelayCount()
# for x in range(0, 300):
#     pixels[x] = (0, 255, 0)
# pixels.show()
# time.sleep(2)
# for x in range(0, 300, 5):
#     pixels[x] = (230, 255, 0)
#     pixels[x + 1] = (230, 255, 0)
#     pixels[x + 2] = (230, 255, 0)
#     pixels[x + 3] = (230, 255, 0)
#     pixels[x + 4] = (230, 255, 0)
#     pixels.show()

# this is here so i know the program is done
# print("hi")
# time.sleep(3)
# pixels.deinit()

