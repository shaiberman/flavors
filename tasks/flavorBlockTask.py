import numpy
from psychopy import visual, event, core, data, gui
from psychopy.hardware import keyboard
import glob
import os
import numpy as np
from utils import * # this used to be "from utils import *"
from manage_info.store_data import *
from manage_subject_info import *
import scipy.io
import serial
import time

'''This script contains the functions the run the tasks in each block'''

# define the arduino connection:
arduino = serial.Serial(port = 'COM4', baudrate = 9600, timeout=0)
# it sometimes takes a sec to connect - so wait for 2 seconds:
time.sleep(2)

f = 'Calibri'

'''
~~~~~~~~~~~~
INSTRUCTIONS
~~~~~~~~~~~~
'''
def flave_instructions(info,win,kb,demo):

    win.color='black' #Black background
    # if scanning - indicate to use the index finger, otherwise - space key
    if info['Scanning (0/1)'] == 1:
        button = "your INDEX finger"
    else:
        button = "the SPACE key"

    # instructon text for dmo vs real things
    if demo == True:
        instructions = "You will do a short demo to experience what the experiment will be like.\n" \
                       "During the next hour, you will taste various flavors.\n" \
                       "Please keep you eyes on the fixation point.\n" \
                       "The fixation will turn green right before the flavor will be administered to your mouth.\n" \
                       "After each flavor you will rinse your mouth with water. During the rinse the fixation will turn blue.\n" \
                   "Press " + button + " to start the demo"
    else:
        instructions = "You will soon start the scan ....\n" \
                      "During the next hour, you will taste various flavors.\n" \
                       "Please keep you eyes on the fixation droplet.\n" \
                       "The fixation will turn blue right before the flavor will be administered to your mouth.\n" \
                       "Press " + button + " to start the scan."
    #"After each flavor you will rinse your mouth with water. During the rinse the fixation will turn blue.\n" \

        # define the text object on the screen
    txt = visual.TextStim(win,text=instructions, font=f,
                          pos=(0.0,0.0), depth=0, rgb=None, color=(1.0, 1.0, 1.0),
                          colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                          ori=0.0, height=0.07, antialias=True, bold=True, italic=False)

    # Present the instruction until the right key is pressed
    kb.clock.reset() # resent the timer of the keyboard
    kl = ['space', '1'] # allowed keys
    keys = kb.getKeys(keyList=kl) # "listen" to keyboard
    while not keys:
        txt.setAutoDraw(True)         # draw instruction on window
        win.flip()                    # display window
        keys = kb.getKeys(keyList=kl) # keep listening

    # if we are her ethat means a key was pressed
    # stop drawing instructions and resent things
    txt.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.3)
    kb.clock.reset()

def betweenBlocks(info,win,kb):

    win.color='black' #Black background
    # if scanning - indicate to use the index finger, otherwise - space key

    instructions = "End of run.. \n Waiting for experimenter.. "
    txt = visual.TextStim(win,text=instructions, font=f,
                          pos=(0.0,0.0), depth=0, rgb=None, color=(1.0, 1.0, 1.0),
                          colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                          ori=0.0, height=0.07, antialias=True, bold=True, italic=False)

    # Present the instruction until the right key is pressed
    kb.clock.reset() # resent the timer of the keyboard
    kl = ['space'] # allowed keys
    keys = kb.getKeys(keyList=kl) # "listen" to keyboard
    while not keys:
        txt.setAutoDraw(True)         # draw instruction on window
        win.flip()                    # display window
        keys = kb.getKeys(keyList=kl) # keep listening

    # if we are her ethat means a key was pressed
    # stop drawing instructions and resent things
    txt.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.3)
    kb.clock.reset()

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
############  TASK   ###########
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def flavorBlock(info,win,kb,flaves,demo,block):

    # flave_instructions(info,win,kb,demo)    # present instructions:
    win.color=[0.5,0.5,0.5]    # change screen baclground to grey
    win.mouseVisible = False   # hide cursor

    # info about the trials timing:
    fr = 60 # frame rate (how many times a second is the screen represhed
    tasteT = 8*fr # 8seconds (400 frames): 5s delivery + extra 3s second to finish swallowing etc.
    rinseT = 4*fr # 2s delivery? + extra 2s?

   # read onset files which contain jitter between trials
    # thee jitter will be 7s on average, drawn from an exponential distribution minmax=[4,12]
    onsetfile = "onsets/flavonset_" + str(random.randint(1, 10)) + ".mat"
    onsetsDict = scipy.io.loadmat(onsetfile)
    onsets = onsetsDict['onsetlist'] # this is the actual onset times, I just want the ITI -
    ITI_s = numpy.diff(onsets[0])    # the ITI is the difference between onsets
    ITI_f_fl = ITI_s * fr            # go from seconds to frames

    # define output path
    if demo == True:
        # (if demo dont save and only take first ITIs
        filename = 'temp'
        ITI_f = ITI_f_fl[0:3]
    else:
        filename = "data/{Subject ID}/wtp_{Subject ID}_{date}".format(**info)

    ITI_f = ITI_f_fl.astype(int) # turn into into integer - there is no "half frame"

    TR_key='5' # if we are scanning - the MRI TR will appear as a 5-key press.

    'screen sections'
    fixation = visual.Rect(win, size=0.04, units='norm', pos=(0, 0), lineColor='black', fillColor='black')
    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)
    # just to test the actual timing - display the seconds that go by
    timer_text = visual.TextStim(win, text='',
                                  font=f, pos=(-0.0, -0.15), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # create a variable that will track trial timing infotmation
    globalClock = core.Clock()
    vol=0
    outputdf = pd.DataFrame({"vol": [vol],
                             "onset": [0.000],
                             "key": ['NaN'],
                             "trial_flavor": [0],
                             "comment": ['start of scanning run']})
    # for i in range(-1 * MR_settings['skip'], 0):
    filename2 = "data/{Subject ID}/Triggers_run".format(**info) + str(block + 1) + "_{Subject ID}_{date}".format(
        **info) + ".csv"
    # use thistrial handler function to save the data
    trials = data.TrialHandler(trialList=list(flaves),nReps=1)
    if demo == False:
    #add trials to the experiment handler to store data
        thisExp = data.ExperimentHandler(
                name='flavors', version='1.0', #not needed, just handy
                extraInfo = info, #the info we created earlier
                dataFileName = filename ) # using our string with data/name_date
        thisExp.addLoop(trials)  # there could be other loops (like practice loop)

    # reset keyboard and if scanning - wait for first TR
    kb.clock.reset()
    kb.clearEvents()
    if demo == False:
        # waitForScanner - allow 2 minutes of waiting...
        wait_screen.setAutoDraw(True)
        win.flip()
        kb.waitKeys(maxWait=120, keyList=TR_key, waitRelease=True, clear=True)
        wait_screen.setAutoDraw(False)
    # mark first TR
    t = globalClock.getTime()
    outputdf.loc[len(outputdf)] = [1, t, TR_key, 'NaN', 'First TR']
    kb.clock.reset()

    # finally - strat looping oer trial and start experiment
    for i, thisTrial in enumerate(flaves):
        secs = 0
        timer_text.setAutoDraw(True)

        fixation.lineColor = 'black'
        fixation.fillColor = 'black'
        fixation.setAutoDraw(True)
        flavor = flaves[i]
        time_of_prep = ITI_f[i]-.5*fr
        TrialT = ITI_f[i]+tasteT+rinseT
        for frames in range(TrialT):
            # bail
            if event.getKeys(['escape']):
                if not demo:
                    outputdf.to_csv(filename2, encoding='utf-8')
                trials.finished = True
                core.quit()

            # listen to TRs
            keys_TR = kb.getKeys(keyList=TR_key)
            if keys_TR:
                vol += 1
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,flavor,'TR']

            # if first frame - add note the trial started
            if frames == 1:
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,flavor,'trial started ']

            if np.mod(frames,60) == 0:
                secs += 1
                timer_text.text = secs.__str__()

            if time_of_prep < frames < ITI_f[i]+tasteT:  # right before flavor flood:
                fixation.lineColor = 'green'
                fixation.fillColor = 'green'

            if  ITI_f[i] == frames :
                print('taste')
                arduino.write(str.encode(flavor))  # LED turned on

            if frames == ITI_f[i] + tasteT:  # give tatste
                arduino.write(str.encode(0))  # LED turned on

            if ITI_f[i]+tasteT < frames < TrialT: # change fixation color, rinse
                fixation.lineColor = 'blue'
                fixation.fillColor = 'blue'

            if frames ==  ITI_f[i]+tasteT or frames ==  ITI_f[i]:
                secs = 0

            win.flip()

        # clear screen     and vars
        win.flip()
        kb.clock.reset()
        kb.clearEvents()

    if demo ==False:
        t = globalClock.getTime()
        outputdf.loc[len(outputdf)] = [vol, t, 'NaN','NaN', 'End of scan']
        outputdf.to_csv(filename2, encoding='utf-8')

    fixation.setAutoDraw(False)
    win.mouseVisible = True
    win.flip()
    kb.clock.reset()
    kb.clearEvents()

    return filename+".csv"



'''
################################################
####################rate Flavors#####################
##################################
################################################
'''

def rate_flavors(info,win,kb, flavors, block):
    win.color = 'black'
    subjectId = info['Subject ID']
    filename = "data/{Subject ID}/flavor_rate".format(**info)+"_{Subject ID}_{date}".format(**info)
    outputdf = pd.DataFrame({"flavor": ['NaN'],
                             "rating": [0.000],
                             "RT": [0.000],
                             "block": [0]})

    mouse = event.Mouse()
    fixation = visual.Rect(win, size=0.04, units='norm', pos=(0, 0), lineColor='black', fillColor='black')

    # question
    mQ = visual.TextStim(win, text='How palatable do you find the following flavor?',wrapWidth=1.8,
                         pos = (0,0.8),height=0.08,bold=True,units='norm',color='white',font=f,)
    Qscale = visual.Slider(win, ticks=(0,50,100),labels = (0,100),
                               pos=[0,-0.25], size=(1,0.08) ,
                               units='norm',style='slider',
                               granularity=0, readOnly=False, color='white')#, fillColor='black')
    timer_text = visual.TextStim(win, text='0',
                                 font=f, pos=(-0.0, -0.2), depth=0, rgb=None, color='white',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    #flavors = range(1,8)
    Qscale.reset()
    kb.clock.reset()
    for i, flavor in enumerate(flavors):
        secs = 0
        fixation.lineColor = [0.5, 0.5, 0.5]
        fixation.fillColor = 'black'
        fixation.setAutoDraw(True)
        mQ.setAutoDraw(True)
        timer_text.setAutoDraw(True)
        # 2 second of waiting..(1.5 second of black fixation)
        # 3 seconds of tasting (3.5 of green fixation)
        # then the scale..  then rinse for 2 seconds.
        for frames in range(300): # 5 seconds

            if np.mod(frames,60) == 0:
                secs += 1
                timer_text.text = secs.__str__()

            # bail
            if event.getKeys(['escape']):
                core.quit()

            if frames > 90:  # right before flavor flood:
                fixation.lineColor = 'green'
                fixation.fillColor = 'green'
            if frames == 120: # should it be bigger than or equal to?
                print('taste')
                # givetaste(flavor)
            win.flip()

        fixation.lineColor = [0.5, 0.5, 0.5]
        fixation.fillColor = 'black'
        Qscale.setAutoDraw(True)
        while not Qscale.rating:
            win.flip()
            # bail option
            keys = kb.getKeys(keyList=['escape'])
            if keys:
                if keys[0].name == 'escape':
                    print('user ended experiment')
                    core.quit()

        if Qscale.rating:
            Response = Qscale.getRating()
            decisionTime = Qscale.getRT()

        core.wait(0.5)
        mQ.setAutoDraw(False)
        win.flip()
        Qscale.reset()
        mouse.clickReset()
        Qscale.setAutoDraw(False)

        #rinse!
        for frames in range(150): # 2.5 seconds
            # bail
            if event.getKeys(['escape']):
                core.quit()

            fixation.lineColor = 'blue'
            fixation.fillColor = 'blue'

            if frames == 30: # or bigger than 30
                print('rinse')
                # givetaste(rinse)
            win.flip()



        # add response info to trial handler
        outputdf.loc[len(outputdf)] = [flavor, Response, decisionTime,block]
    outputdf.to_csv(filename, encoding='utf-8')
    Qscale.setAutoDraw(False)
    mQ.setAutoDraw(False)
    win.flip()
    return filename + ".csv"


''' make a test for pilot'''

def flavorBlockTest_test(info,win,kb,demo,block):
    if block==0:
        flave_instructions(info, win, kb, demo)
    win.color = [0.5, 0.5, 0.5]
    win.mouseVisible = False  # hide cursor
    win.flip()
    filename = "data/{Subject ID}/flavor_test_{Subject ID}_{date}".format(**info) + '_run' + str(block)
    outputdf = pd.DataFrame({"Vol": [0.0],
                             "Time": [0.000],
                             "Key": ['NaN'],
                             'Flavor':['NaN'],
                             "Event": ['NaN']})

    # info about the trials timing!
    fr = 60
    tasteT = 2 * fr  # 2s delivery + we take into account extra 3s second to finish swallowing etc.
    onsetfile = "onsets/flavonset_" + str(random.randint(1, 10)) + ".mat"
    onsetsDict = scipy.io.loadmat(onsetfile)
    onsets = onsetsDict['onsetlist']  # this is the actual onset times, I just want the ITI -
    ITI_s = numpy.diff(onsets[0])  # the ITI is the difference between onsets
    ITI_f_fl = ITI_s * fr  # go from seconds to frames
    ITI_f = ITI_f_fl.astype(int)  # turn into into integer - there is no "half frame"
    # these are 30! onsets..
    # they include the 5 second event time
    # they amount to 5.633mnutes (225 * 1.5sTRs, i think)
    fixation_tstb = visual.ImageStim(win, image='imgs/drop_black.png', ori=0, pos=[0, 0], size=(108 / 5, 143 / 5),
                                     units='pix')
    fixation_tstgo = visual.ImageStim(win, image='imgs/drop_blue.png', ori=0, pos=[0, 0], size=(108 / 5, 143 / 5),
                                      units='pix')

    fixation = visual.Rect(win, size=0.04, units='norm', pos=(0, 0), lineColor='black', fillColor='black')
    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f, pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)
    timer_text = visual.TextStim(win, text='',
                                 font=f, pos=(-0.0, -0.15), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    globalClock = core.Clock()

    # reset keyboard
    kb.clock.reset()
    kb.clearEvents()
    # read trialList from CSV
    vol = 0
    TR_key = '5'
    if demo==False:
        # waitForScanner - allow 2 minutes of waiting...
        t = globalClock.getTime()
        wait_screen.setAutoDraw(True)
        win.flip()
        kb.waitKeys(maxWait=120, keyList=[TR_key], waitRelease=True, clear=True)
        wait_screen.setAutoDraw(False)

        outputdf.loc[len(outputdf)] = [1, t, TR_key, 'NaN', 'First TR']
        kb.clock.reset()

        '''PRE EXP COUNTDOWN'''
        countDown=10
        timer_text = visual.TextStim(win, text=countDown.__str__(),
                                     font=f, pos=(0, 0), depth=0, rgb=None, color='black',
                                     colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                     ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

        # display     countdown    numbers
        secs = 10
        timer_text.text = secs.__str__()
        timer_text.setAutoDraw(True)
        win.flip()
        for frames in range(countDown * 60):
            if np.mod(frames, 60) == 0:
                secs -= 1
                timer_text.text = secs.__str__()
            win.flip()
        timer_text.setAutoDraw(False)
        win.flip()
        kb.clock.reset()

    # assign response key for accurate first RT
    if demo==True:
        trialNum = 2
    else:
        trialNum = len(ITI_f)

    vol=0
    for i in range(trialNum):
        secs = 0
        #timer_text.setAutoDraw(True)

        fixation.lineColor = 'black'
        fixation.fillColor = 'black'
        #fixation.setAutoDraw(True)
        flavor = "a"
        #time_of_prep = ITI_f[i] - .5 * fr
        TrialT = ITI_f[i] # this is the length of the trial - it varies
        for frames in range(int(TrialT)):
            # bail
            if event.getKeys(['escape']):
                outputdf.to_csv(filename, encoding='utf-8')
                core.quit()

            # TR
            keys_TR = kb.getKeys(keyList=TR_key)
            if keys_TR:
                vol += 1
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,'NaN', 'TR']

            # second timer
            if np.mod(frames, 60) == 0:
                secs += 1
                timer_text.text = secs.__str__()

            if 60<frames<210:# time_of_prep < frames < ITI_f[i] + tasteT:  # right before flavor flood:
                #fixation.lineColor = 'green'
                #fixation.fillColor = 'green'
                fixation_tstb.setAutoDraw(False)
                fixation_tstgo.setAutoDraw(True)
            else:
                fixation_tstgo.setAutoDraw(False)
                fixation_tstb.setAutoDraw(True)

            if frames==90:# ITI_f[i] == frames:
                arduino.write(str.encode(flavor))  # LED turned on
                print(str(frames)+'here we should give flavor')
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,'NaN',flavor, 'flavor']

            #if frames == ITI_f[i] + tasteT or frames == ITI_f[i]:
            #    secs = 0

            win.flip()

        # clear screen     and vars
        win.flip()
        kb.clock.reset()
        kb.clearEvents()
        timenow = globalClock.getTime()

    outputdf.to_csv(filename, encoding='utf-8')

    fixation_tstgo.setAutoDraw(False)
    fixation_tstb.setAutoDraw(False)
    win.mouseVisible = True
    win.flip()
    kb.clock.reset()
    kb.clearEvents()

    return


def flavorBlockTest(info,win,kb):
    flaves = ["a","a" "a","a"]
    win.color=[0.5,0.5,0.5]
    win.mouseVisible = False   # hide cursor

    # info about the trials timing!
    fr = 60
    tasteT = 8*fr # 5s delivery + extra 3s second to finish swallowing etc.
    rinseT = 4*fr # 2s delivery? + extra 2s?

    ITI_f =[6*60, 8*60]

    fixation = visual.Rect(win, size=0.04, units='norm', pos=(0, 0), lineColor='black', fillColor='black')
    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)
    timer_text = visual.TextStim(win, text='',
                                  font=f, pos=(-0.0, -0.15), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    globalClock = core.Clock()

    # reset keyboard
    kb.clock.reset()
    kb.clearEvents()
    # read trialList from CSV
    vol=0

    # assign response key for accurate first RT
    for i, thisTrial in enumerate(flaves):
        secs = 0
        timer_text.setAutoDraw(True)

        fixation.lineColor = 'black'
        fixation.fillColor = 'black'
        fixation.setAutoDraw(True)
        flavor = flaves[i]
        time_of_prep = ITI_f[i]-.5*fr
        TrialT = ITI_f[i]+tasteT+rinseT
        for frames in range(TrialT):
            # bail
            if event.getKeys(['escape']):
                core.quit()

            # second timer
            if np.mod(frames,60) == 0:
                secs += 1
                timer_text.text = secs.__str__()

            if time_of_prep < frames < ITI_f[i]+tasteT:  # right before flavor flood:
                fixation.lineColor = 'green'
                fixation.fillColor = 'green'

            if  ITI_f[i] == frames :
                arduino.write(str.encode(flavor))  # LED turned on

            if ITI_f[i]+tasteT < frames < TrialT: # change fixation color, rinse
                fixation.lineColor = 'blue'
                fixation.fillColor = 'blue'

            if frames ==  ITI_f[i]+tasteT or frames ==  ITI_f[i]:
                secs = 0

            win.flip()

        # clear screen     and vars
        win.flip()
        kb.clock.reset()
        kb.clearEvents()


    fixation.setAutoDraw(False)
    win.mouseVisible = True
    win.flip()
    kb.clock.reset()
    kb.clearEvents()

    return






