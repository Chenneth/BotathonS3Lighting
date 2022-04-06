import ctypes

import neopixel
import board
import time
import multiprocessing
import configparser
import atexit

#setting up config settings... should this go in the main block?
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
    "LowTimeColor": "00FCFC",
    "GoalScored": "0000FF",
    "TimeUp": "FF0000",
    "IdleOne": "FFFFFF",
    "IdleTwo": "00853E", #this is UNT Green (according to https://identityguide.unt.edu/create-our-look/color)
    "ShootOutOne": "FFD700",
    "ShootOutTwo":"FFFFFF",
    "SuddenDeath":"FF0000",
    "LEDCount": "300"
}

# color configs
temp = config.get("COLORS", "Countdown")
COLOR_COUNTDOWN = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "TimerNormal")
COLOR_TIMER = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "LowTimeColor")
COLOR_LOWTIME = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "GoalScored")
COLOR_GOALSCORED = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "TimeUp")
COLOR_TIMEUP = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "IdleOne")
COLOR_IDLEONE = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "IdleTwo")
COLOR_IDLETWO = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

temp = config.get("COLORS", "ShootOutOne")
COLOR_SOONE = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))
temp = config.get("COLORS", "ShootOutTwo")
COLOR_SOTWO = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))


temp = config.get("COLORS", "SuddenDeath")
COLOR_SD = (int(temp[:2], 16), int(temp[2:4], 16), int(temp[4:6], 16))

# behavior configs
STARTCOUNTDOWN = config.getboolean("BEHAVIOR", "StartCountdown")
YELLOWSWITCH = config.getint("BEHAVIOR", "YellowSwitch")
AUTOTERM = config.getint("BEHAVIOR", "AutoTerm")
IDLELIGHTS = config.getboolean("BEHAVIOR", "IdleLights")

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
    pixels.brightness = 1.0
    pixels.fill((0,0,0))
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
        pixels.brightness-=.05
        pixels.show()
        time.sleep(.05)
    pixels.fill((0,0,0))
    pixels.brightness=1.0
    pixels.show()

#please give this 'pipeBack' and not 'pipeFront' (it shouldn't matter but keep it consistent)
def Countdown_Normal(pipe:multiprocessing.connection):
    pixels.fill(COLOR_TIMER)
    pixels.brightness = 1.0
    pixels.show()
    totalSeconds = TIMERTIME
    while totalSeconds > LOWTIME and totalSeconds>-1:  # 30 seconds is when it switches to yellow
        time.sleep(.1)
        totalSeconds -= .1
        if pipe.poll():
            msg = pipe.recv()
            print(msg)
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:])
                    print("Total time is now {}".format(totalSeconds))
                except (TypeError, ValueError):
                    print("Could not add the timer due to an error")
            elif msg[:1]=="v":
                print("Current time on the timer is {} seconds".format(totalSeconds))
            elif msg[:1]=="p":
                print("Timer currently paused. Waiting.\n")
                pixels.fill((47,47,79))
                pixels.brightness = .3
                pixels.show()
                ResumePlay(pipe)
            elif msg[:1]=="g":
                Goal()
                ResumePlay(pipe)
            else:
                print("\nNot a valid input.\n")
            pipe.send("start up b")
    if YELLOWSWITCH==1:
        start = time.time()
        offset = 0.0
        for x in range(300):
            pixels[x] = (COLOR_LOWTIME)
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
                    except (TypeError, ValueError):
                        print("Could not add the timer due to an error")
                elif msg[:1]=="v":
                    print("Current time on the timer is {} seconds".format(totalSeconds))
                elif msg[:1]=="p" or msg[:1]=="g":

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
                pipe.send("start up b")

            #exit animation if it takes more time than the current timer has
            if (time.time()-start-offset)>=totalSeconds:
                break
        totalSeconds -= float(time.time()-start - offset)
    elif YELLOWSWITCH==2:
        pixels.fill(COLOR_LOWTIME)
        pixels.show()
    #todo: Should this be 0 or -1?
    while totalSeconds > -1:  # 30 seconds is when it switches to yellow
        time.sleep(.1)
        totalSeconds -= .1
        if pipe.poll():
            msg = pipe.recv()
            #add time to the timer, i really don't feel like fixing the colors on this though, will ask seb
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:])
                    print("Total time is now {}".format(totalSeconds))
                except (TypeError, ValueError):
                    print("Could not add the timer due to an error")
            elif msg[:1]=="v":
                print("Current time on the timer is {} seconds".format(totalSeconds))
            elif msg[:1] == "p":
                print("Timer currently paused. Waiting.\n")
                pixels.fill((47, 47, 79))
                pixels.brightness = .3
                pixels.show()
                ResumePlay(pipe,prevColor= (COLOR_TIMER if YELLOWSWITCH==0 else COLOR_LOWTIME))
            elif msg[:1] == "g":
                Goal()
                ResumePlay(pipe,prevColor= (COLOR_TIMER if YELLOWSWITCH==0 else COLOR_LOWTIME))
            else:
                print("\nNot a valid input.\n")
            pipe.send("start up")
    pixels.fill(COLOR_TIMEUP)
    pixels.brightness = 0.5 #idk if you want me to have the brightness in the conf files too
    pixels.show()

    print("Time's up. Enter any key to move to the next dialogue. Lights will turn off immediately.\n")

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
                "'g'\tGoal was scored\n"
                "'v'\tView current time on timer\n")
        pipe.send(msg)
        #sleep for 1.1 seconds to ensure that the other process receives the input instead of this one
        time.sleep(.2)
        if msg[:1]=='p' or msg[:1]=='g':
        #pause or goal scored
            secmsg = input("Press enter to continue...\n")
            pipe.send(secmsg)
        # i know this prevents rapid pausing and unpausing... but i don't have a good way to test this rn
        #wait for the process to restart or whatever you want to call it
        while timerProcess.is_alive() and not pipe.poll():
            time.sleep(.1)
    pixels.brightness = 0.0
    pixels.fill((0,0,0))
    pixels.show()

def SuddenDeath(pipe:multiprocessing.connection):
    pixels.fill(COLOR_SD)
    #startTime = time.time()

    goingDown = True
    brightness = 1.0 #this is probably not necessary... but if it ain't broke....
    pixels.brightness = 1.0
    pixels.show()
    totalSeconds = float(SDTIME)
    while SDTIME > -1.0:
        brightness = brightness - .025 if goingDown else brightness + .025
        if brightness < .2:
            goingDown = False
        elif brightness > .9:
            goingDown = True
        pixels.brightness = brightness
        pixels.show()
        time.sleep(0.05)
        totalSeconds -= 0.05
        if pipe.poll():
            msg = pipe.recv()
            print(msg)
            if msg[:1]=="a":
                try:
                    totalSeconds += int(msg[2:])
                    print("Total time is now {}".format(totalSeconds))
                except (TypeError, ValueError):
                    print("Could not add the timer due to an error")
            elif msg[:1]=="v":
                print("Current time on the timer is {} seconds".format(totalSeconds))
            elif msg[:1]=="p":
                print("Timer currently paused. Waiting.\n")
                pixels.fill((47,47,79))
                pixels.brightness = .3
                pixels.show()
                ResumePlay(pipe, prevColor=COLOR_SD)
            elif msg[:1]=="g":
                Goal()
                return #i could probably design this without a break... BUT I'm ~outta time~ lazy
            pipe.send("bbbb")

    pixels.fill(255,255,255)
    pixels.brightness = 1.0
    pixels.show()
    print("Sudden Death is over. Enter any key to continue.\n")

def ResumePlay(pipe:multiprocessing.connection, prevColor = COLOR_TIMER):
    pipe.recv()
    pixels.fill((0, 0, 0))
    pixels.brightness = 1.0
    pixels.show()
    print("Resuming timer.")
    StartDelayCount()
    pixels.fill(prevColor)
    pixels.show()

def SwapColors(pipe:multiprocessing.connection, colorOne:(int,int,int),colorTwo:(int,int,int)):
    pixels.brightness = 1.0
    for x in range(0,300,2):
        pixels[x] = colorOne
        pixels[x+1] = colorTwo
    timeSinceLastSwitch = 0.0
    colorSwap = False
    pixels.show()
    #this loop should swap the colors between ShootOut colors one and two
    #while no message is sent from the other end
    while not pipe.poll():
        time.sleep(0.1)

        timeSinceLastSwitch+=0.1
        if timeSinceLastSwitch>=0.5:
            if colorSwap:
                for x in range(0, 300, 2):
                    pixels[x] = colorOne
                    pixels[x + 1] = colorTwo
            else:
                for x in range(0, 300, 2):
                    pixels[x] = colorTwo
                    pixels[x + 1] = colorOne
            timeSinceLastSwitch = 0.0
            colorSwap = not colorSwap
            pixels.show()


#defining a method for this probably isnt necessary
def ShootOutInput(pipe:multiprocessing.connection):
    msg = input("\nPress enter to exit shootout mode.\n")
    pipe.send(msg)

def StartTimer():
    if STARTCOUNTDOWN:
        StartDelayCount()
    # idk how to use Pools so I won't
    timerProcess = multiprocessing.Process(target=Countdown_Normal, args=[pipeBack])
    # inputProcess = multiprocessing.Process(target=TimerInput,args=[queue])
    processes.append(timerProcess)
    timerProcess.start()
    # inputProcess.start()
    # am i doing this right?
    # timerProcess.join()
    TimerInput(timerProcess, pipeFront)
    timerProcess.close()
    EmptyPipes(pipeFront,pipeBack)
    processes.pop(0)

def EmptyPipes(PipeFront:multiprocessing.connection, PipeBack:multiprocessing.connection):
    # clearing out the pipes... there shouldn't be more than a single message per end
    while PipeFront.poll():
        PipeFront.recv()
    while PipeBack.poll():
        PipeBack.recv()

def StartSuddenDeath(PipeFront:multiprocessing.connection, PipeBack:multiprocessing.connection):
    sdProcess = multiprocessing.Process(target=SuddenDeath, args=[PipeBack])
    # yes i ctrlc ctrlv the next 9 lines, no i am not removing the comments
    # inputProcess = multiprocessing.Process(target=TimerInput, args=[queue])
    StartDelayCount()
    sdProcess.start()
    processes.append(sdProcess)
    TimerInput(sdProcess, PipeFront)
    # inputProcess.start()
    # am i doing this right?
    # timerProcess.join()

    sdProcess.close()
    EmptyPipes(PipeFront, PipeBack)
    processes.pop(0)

def StartIdle(PipeFront:multiprocessing.connection, PipeBack:multiprocessing.connection):
    idleProcess = multiprocessing.Process(target=SwapColors, args=[PipeBack, COLOR_IDLEONE, COLOR_IDLETWO])
    idleProcess.start()
    processes.append(idleProcess)
    msg = input("\nPress enter to start the timer.\n")
    PipeFront.send(msg)
    idleProcess.join()
    idleProcess.close()
    EmptyPipes(PipeFront, PipeBack)
    processes.pop(0)

def StartShootOut(PipeFront:multiprocessing.connection, PipeBack:multiprocessing.connection):
    sOProcess = multiprocessing.Process(target=SwapColors, args=[PipeBack, COLOR_SOONE, COLOR_SOTWO])
    sOProcess.start()
    processes.append(sOProcess)
    ShootOutInput(PipeFront)
    sOProcess.join()
    sOProcess.close()
    EmptyPipes(PipeFront, PipeBack)
    processes.pop(0)

if __name__=='__main__':
    atexit.register(at_exit)
    print("\nCurrent config values:\n")
    for sect in config.sections():
        print("\n\nSection [{}]:\n".format(str(sect)))
        for key,val in config.items(sect):
            print("{} = {}\n".format(key,val))
    if STARTCOUNTDOWN:
        print("This timer will have a 3 second countdown before starting.\n")
    else:
        print("Timer will start as soon as user inputs...maybe idk\n")
    #idk if terminal will allow it (because it didn't work with C++)
    input("Press 'enter' to start\n")
    continueProgram = True
    if AUTOTERM!=1:
        while continueProgram:
            StartTimer()
            #ask if sudden death
            MatchOver
            while True:
                MatchOver = input("\nIs the match over? Enter 0 to reset the timer, 1 to start sudden death, or 2 to turn off all LEDs and terminate the program.\nSudden death will start with a countdown.\n")
                if MatchOver[:1]=='0' or MatchOver[:1]=='1' or MatchOver[:1]=='2':
                    break
            if MatchOver[:1]=='2': #terminate program
                continueProgram=False

            elif MatchOver[:1]=='1': #sudden death
                StartSuddenDeath(pipeFront,pipeBack)
                while True:
                    MatchOver = input("\nIs the match over? Enter 0 to reset the timer, 1 to start Shoot-Out, or 2 to turn off all LEDs and terminate the program.\n")
                    if MatchOver[:1]=='0' or MatchOver[:1]=='1' or MatchOver[:1]=='2':
                        break
                if MatchOver[:1] == '1':
                    StartShootOut(pipeFront,pipeBack)
                    if IDLELIGHTS:
                        StartIdle(pipeFront,pipeBack)
                    else:
                        input("\nPress Enter to start the timer.\n")
                elif MatchOver[:1] == '2':
                    continueProgram = False #should i change this to break
                else:
                    if IDLELIGHTS:
                        StartIdle(pipeFront, pipeBack)
                    else:
                        input("\nPress Enter to start the timer.\n")

            else:
                if IDLELIGHTS:
                    StartIdle(pipeFront, pipeBack)
                else:
                    input("\nPress Enter to start the timer.\n")
    else:
        StartTimer()
        # ask if sudden death
        while True:
            MatchOver = input("Is the match over? Enter 0 to start sudden death, or anything else to exit.\nSudden death will start with a 3 second countdown.\n")
            if MatchOver[:1] == '0' or MatchOver[:1] == '1' or MatchOver[:1] == '2':
                break
        if MatchOver[:1] == '0':  # sudden death
            StartSuddenDeath(pipeFront,pipeBack)
            while True:
                MatchOver = input("\nIs the match over? Enter 0 to start Shoot-Out, or anything else to exit.\n")
                if MatchOver[:1]=='0' or MatchOver[:1]=='1' or MatchOver[:1]=='2':
                    break
            if MatchOver[:1] == '0':
                StartShootOut(pipeFront, pipeBack)
        print("exiting")

    pixels.deinit() #i thought that this would need more than 1 line lmao