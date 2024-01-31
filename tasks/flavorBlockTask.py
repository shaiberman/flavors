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

arduino = serial.Serial(port = 'COM4', baudrate = 9600, timeout=0)

time.sleep(2)
'''
if x:
    arduino.write(str.encode('1')) # LED turned on
    time.sleep(1)
if y:
    arduino.write(str.encode('0')) # LED turned off
    % this is prett good: https://forum.arduino.cc/t/serial-input-basics-updated/382007
'''

f = 'Calibri'

'''
~~~~~~~~~~~~
INSTRUCTIONS
~~~~~~~~~~~~
'''
def flave_instructions(info,win,kb,demo):

    win.color='black'
    if info['Scanning (0/1)'] == 1:
        button = "your INDEX finger"
    else:
        button = "the SPACE key"

    if demo == True:
        instructions = "You will do a short demo to experience what the experiment will be like.\n" \
                       "During the next hour, you will taste various flavors.\n" \
                       "Please keep you eyes on the fixation point.\n" \
                       "The fixation will turn green right before the flavor will be administered to your mouth.\n" \
                       "After each flavor you will rinse your mouth with water. During the rinse the fixation will turn blue.\n" \
                   "Press " + button + " to start the demo"
    else:
        instructions = "You will now start the scan. a reminder:start a tasting task about ....\n" \
                      "During the next hour, you will taste various flavors.\n" \
                       "Please keep you eyes on the fixation point.\n" \
                       "The fixation will turn green right before the flavor will be administered to your mouth.\n" \
                       "After each flavor you will rinse your mouth with water. During the rinse the fixation will turn blue.\n" \
                       "Press " + button + " to start the scan."

    txt = visual.TextStim(win,text=instructions, font=f,
                          pos=(0.0,0.0), depth=0, rgb=None, color=(1.0, 1.0, 1.0),
                          colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                          ori=0.0, height=0.07, antialias=True, bold=True, italic=False)

    # MAIN INSTRUCTIONS
    kb.clock.reset()
    kl = ['space', '1']
    keys = kb.getKeys(keyList=kl)
    while not keys:
        txt.setAutoDraw(True)
        win.flip()
        keys = kb.getKeys(keyList=kl)

    txt.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.3)
    kb.clock.reset()

'''


############  TASK   ###########


'''
def flavorBlock(info,win,kb,flaves,demo,block):

    flave_instructions(info, win, kb, demo)
    win.color=[0.5,0.5,0.5]
    win.mouseVisible = False   # hide cursor

    # info about the trials timing!
    fr = 60
    tasteT = 8*fr # 5s delivery + extra 3s second to finish swallowing etc.
    rinseT = 4*fr # 2s delivery? + extra 2s?

   # the onsets should just be the jitter. on top of it I will add 0.5 s prep and 5 second tasting..
    onsetfile = "onsets/flavonset_" + str(random.randint(1, 10)) + ".mat"
    onsetsDict = scipy.io.loadmat(onsetfile)
    onsets = onsetsDict['onsetlist']
    random.shuffle(onsets)
    ITI_s = numpy.diff(onsets[0])
    ITI_f_fl = ITI_s * fr

    # load Questions and start output log
    if demo == True:
        filename = 'temp'
        ITI_f = ITI_f_fl[0:3]
    else:
        filename = "data/{Subject ID}/wtp_{Subject ID}_{date}".format(**info)

    ITI_f = ITI_f_fl.astype(int)
    TR_key='5'

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
    outputdf = pd.DataFrame({"vol": [0],
                             "onset": [0.000],
                             "key": ['NaN'],
                             "trial_flavor": [0],
                             "comment": ['start of scanning run']})
    # for i in range(-1 * MR_settings['skip'], 0):
    filename2 = "data/{Subject ID}/Triggers_run".format(**info) + str(block + 1) + "_{Subject ID}_{date}".format(
        **info) + ".csv"

    # reset keyboard
    kb.clock.reset()
    kb.clearEvents()
    # read trialList from CSV
    vol=0
    trials = data.TrialHandler(trialList=list(flaves),nReps=1)
    if demo == False:
    #add trials to the experiment handler to store data
        thisExp = data.ExperimentHandler(
                name='wtp', version='1.0', #not needed, just handy
                extraInfo = info, #the info we created earlier
                dataFileName = filename ) # using our string with data/name_date
        thisExp.addLoop(trials)  # there could be other loops (like practice loop)

        # waitForScanner - allow 2 minutes of waiting...
        wait_screen.setAutoDraw(True)
        win.flip()
        kb.waitKeys(maxWait=120, keyList=TR_key, waitRelease=True, clear=True)
        wait_screen.setAutoDraw(False)
    t = globalClock.getTime()
    outputdf.loc[len(outputdf)] = [1, t, TR_key, 'NaN', 'First TR']

    # assign response key for accurate first RT
    kb.clock.reset()
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



def flavorBlockTest(info,win,kb):
    flaves = ["a","b"]
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






