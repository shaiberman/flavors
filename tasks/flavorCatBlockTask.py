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
#arduino = serial.Serial(port = 'COM4', baudrate = 9600, timeout=0)
# it sometimes takes a sec to connect - so wait for 2 seconds:
time.sleep(2)

f = 'Calibri'

'''
~~~~~~~~~~~~
INSTRUCTIONS
~~~~~~~~~~~~
'''
def flaveCat_instructions(info,win,kb,demo):

    win.color='black' #Black background
    # if scanning - indicate to use the index finger, otherwise - space key
    if info['Scanning (0/1)'] == 1:
        button = "your INDEX finger"
    else:
        button = "the SPACE key"

    # instructon text for dmo vs real things
    if demo == True:
        instructions = "During the next 30 minutes, you will taste various flavors and see several images.\n" \
                       "The flavors and images are paired with each other, such that:\n" \
                       "In each trial you will either see an image or be delivered something to taste. " \
                       "  when delivered a specific flavor, the following image will always be the same\n" \
                       "  and given a specific image, the following flavor will be the same.\n" \
                       "The beginning of each trial will be marked by the fixation turning green. " \
                       "The fixation before an image will be sqare, and the one before taste delivery will be circle.  " \
                       "The fixation will turn green right before the flavor will be administered to your mouth.\n" \
                       "After each flavor you will rinse your mouth with water. During the rinse the fixation will turn blue.\n" \
                       "Please keep you eyes on the fixation point.\n" \
                       "Press " + button + " to start a short demo"
    else:
        instructions = "You will now start the scan.\n " \
                       "Press " + button + " to start the scan."

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


def flaveCat_memory_instructions(info,win,kb,demo):

    win.color='black' #Black background
    # if scanning - indicate to use the index finger, otherwise - space key
    if info['Scanning (0/1)'] == 1:
        button = "your INDEX finger"
        buttonL = "your INDEX finger"
        buttonR = "your MIDDLE finger"
    else:
        button = "the SPACE key"
        buttonL = "the t key"
        buttonR = "the y key"


    # instructon text for dmo vs real things
    instructions = "Your memory will now be tested.\n" \
                   "You will be given the flavors and then be presented wth 2 images" \
                   "Please choose the correct image. \n" \
                   "If the associated image is on the RIGHT, press " + buttonR + ".\n" \
                   "If the associated image is on the lEFT, press " + buttonL + ".\n" \
                   "You will have 2.5 seconds to make the choice. \n" \
                   "Right before the taste delivery the fixation will turn blue. \n" \
                   "Press " + button + " to start a short demo"


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

    # if we are here that means a key was pressed
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
def FlavorCatBlock(info,win,kb,flaves,demo,block):

    # (info, win, kb, demo)    # present instructions:
    win.color=[0.5,0.5,0.5]    # change screen baclground to grey
    win.mouseVisible = False   # hide cursor

    # info about the trials timing:
    fr = 60 # frame rate (how many times a second is the screen represhed
    tasteT = 5*fr # 8seconds (400 frames): 3s delivery + extra 2s second to finish swallowing etc.
    rinseT = 4*fr # 2s delivery? + extra 2s?
    imT  = 1*fr # show visual stimulus for 1s?
    fixT = 0.5*fr # 0.5s just to note a new trial is starting

   # read onset files which contain jitter between trials
    # thee jitter will be 7s on average, drawn from an exponential distribution minmax=[4,12]
    # one onset file for flavors and anoter for tates
    onsetfile = "onsets/flavonset_" + str(random.randint(1, 10)) + ".mat"
    onsetsDict = scipy.io.loadmat(onsetfile)
    onsets = onsetsDict['onsetlist'] # this is the actual onset times, I just want the ITI -
    ITI = fr * np.diff(onsets[0])    # the ITI is the difference between onsets
    ITIfl = ITI.astype(int) # turn into into integer - there is no "half frame"
    ITIim = ITIfl.copy()
    random.shuffle(ITIim)

    # define output path
    if demo == True:
        # (if demo dont save and only take first ITIs
        filename = 'temp'
        ITIfl = ITI[0:3]
        ITIim = ITIfl
    else:
        filename = "data/{Subject ID}/{date}/{Subject ID}_wtp".format(**info)

    TR_key='5' # if we are scanning - the MRI TR will appear as a 5-key press.

    'screen sections'
    fixation_vis = visual.Rect(win, size=20, pos=(0, 0), lineColor='black', fillColor='black', units='pix')
    fixation_ons = visual.TextStim(win, text='+',pos=(0,0),color='black',units='pix',height=200)
    #fixation_tst = visual.Circle(win, ori=0,pos=[0,0], radius = 10,lineColor= 'black', fillColor= 'black',units='pix')
    fixation_tstb = visual.ImageStim(win,  image='imgs/drop_black.png',ori=0, pos=[0, 0], size=(108/5,143/5), units='pix')
    fixation_tstgo = visual.ImageStim(win, image='imgs/drop_blue.png', ori=0, pos=[0, 0], size=(108/5,143/5), units='pix')

    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # just to test the actual timing - display the seconds that go by
    timer_text = visual.TextStim(win, text='',
                                  font=f, pos=(-0.0, -0.15), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # load the images in order
    expVariable = get_pair_info(N=5, block=1) # first block - will determine pairing, 5 repeats of each pair. overall 30 trials.
    df =pd.DataFrame(expVariable) # ['TrialType', 'TrialNum', 'Image', 'flavor', 'flavorCode', 'ImPath']
    Trialtype = df['TrialType'].tolist()
    ImageNames = df['ImPath'].tolist()
    FlavorCodes = df['flavorCode'].tolist()
    images = []
    for file in ImageNames:
        images.append(visual.ImageStim(win=win, image=file, pos=(0, 0),size=(0.6, 0.9), units='norm'))

    # create a variable that will track trial timing infotmation
    globalClock = core.Clock()
    vol=0
    outputdf = pd.DataFrame({"vol": [vol],
                             "onset": [0.000],
                             "key": ['NaN'],
                             "trial_flavor": [0],
                             "comment": ['start of scanning run']})

    # for i in range(-1 * MR_settings['skip'], 0):
    filename2 = "data/{Subject ID}/{date}/Triggers_run".format(**info) + str(block + 1) + ".csv"
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

    if demo:
        Trialtype = Trialtype[0:2]

    # finally - strat looping oer trial and start experiment
    for i, thisTrial in enumerate(Trialtype):
        im = images[i]
        fl = FlavorCodes[i]

        time_of_prep = ITIfl[i] - .5 * fr
        TrialT = ITIfl[i] + tasteT + ITIim[i] + imT + fixT # jitter+taste and rinse + 1sec mage view
        secs = 0
        #timer_text.setAutoDraw(True)
        TrialT=  TrialT.astype(int)
        fixation_ons.setAutoDraw(True)  # trial onset fixation

        for frames in range(TrialT):
            if thisTrial == 'flavorFirst':
                if frames == fixT:
                    fixation_ons.setAutoDraw(False)
                    fixation_tstb.setAutoDraw(True)
                elif frames == fixT + time_of_prep: #fixT < frames < fixT + time_of_prep:  # jitter before the taste
                    fixation_tstb.setAutoDraw(False)
                    fixation_tstgo.setAutoDraw(True)
                elif frames == fixT + ITIfl[i]: # deliver taste
                    print('deliver taste')
                    # arduino.write(str.encode(fl))  # LED turned on
                elif frames == fixT + ITIfl[i] + tasteT : #fixT + ITIfl + tasteT < frames <  fixT + ITIfl + tasteT + ITIim : # fixation for image
                    fixation_tstgo.setAutoDraw(False)
                    fixation_vis.setAutoDraw(True)
                elif frames == fixT + ITIfl[i] + tasteT + ITIim[i]: # fixT + ITIfl[i] + tasteT + ITIim[i] < frames < fixT + ITIfl[i] + tasteT + ITIim[i] + imT: # draw image
                    fixation_vis.setAutoDraw(False)
                    im.setAutoDraw(True)

            elif thisTrial == 'imageFirst':
                if frames == fixT: # + time_of_prep: #fixT < frames < fixT + time_of_prep:  # jitter before the taste
                    fixation_ons.setAutoDraw(False)
                    fixation_vis.setAutoDraw(True)
                elif frames == fixT + ITIim[i]: # fixT+ time_of_prep < frames < fixT + ITIfl[i]: # turn green for prep
                    fixation_vis.setAutoDraw(False)
                    im.setAutoDraw(True)
                elif frames == fixT + ITIim[i] + imT:  # fixT+ time_of_prep < frames < fixT + ITIfl[i]: # turn green for prep
                    im.setAutoDraw(False)
                    fixation_tstb.setAutoDraw(True)
                elif frames == fixT + ITIim[i] + imT +ITIfl[i]-30:
                    fixation_tstb.setAutoDraw(False)
                    fixation_tstgo.setAutoDraw(True)
                elif frames == fixT  + ITIim[i] + imT + ITIfl[i]: # deliver taste
                    print('deliver taste')
                    # arduino.write(str.encode(fl))  # LED turned on
                elif frames == fixT + ITIim[i] + imT + ITIfl[i] + tasteT: #fixT + ITIfl + tasteT < frames <  fixT + ITIfl + tasteT + ITIim : # fixation for image
                    fixation_tstgo.setAutoDraw(False)

            # bail
            if event.getKeys(['escape']):
                core.quit()

            # listen to TRs
            keys_TR = kb.getKeys(keyList=TR_key)
            if keys_TR:
                vol += 1
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,fl,'TR']

            # if first frame - add note the trial started
            if frames == 1:
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,fl,'trial started ']

            if np.mod(frames,60) == 0:
                secs += 1
                timer_text.text = secs.__str__()

            win.flip()

        # clear screen     and vars
        fixation_tstgo.setAutoDraw(False)
        fixation_vis.setAutoDraw(False)
        im.setAutoDraw(False)
        win.flip()
        kb.clock.reset()
        kb.clearEvents()

    if demo == False:
        t = globalClock.getTime()
        outputdf.loc[len(outputdf)] = [vol, t, 'NaN','NaN', 'End of scan']
        outputdf.to_csv(filename2, encoding='utf-8')

    fixation_ons.setAutoDraw(False)
    win.mouseVisible = True
    win.flip()
    kb.clock.reset()
    kb.clearEvents()

    return filename+".csv"

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#################################
############  MEMORY  ###########
############## TEST #############
#################################
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def FlavorCatBlockMemTest(info,win,kb,flaves,demo,block):

    # (info, win, kb, demo)    # present instructions:
    win.color=[0.5,0.5,0.5]    # change screen baclground to grey
    win.mouseVisible = False   # hide cursor

    if info['Scanning (0/1)']==0:
        kl = ['t', 'y'] # allowed keys
    else:
        kl = ['1','2']
        TR_key = '5'  # if we are scanning - the MRI TR will appear as a 5-key press.


    # info about the trials timing:
    fr = 60 # frame rate (how many times a second is the screen represhed
    tasteT = 5*fr # 8seconds (400 frames): 3s delivery + extra 2s second to finish swallowing etc.
    rinseT = 4*fr # 2s delivery? + extra 2s?
    imT  = 1*fr # show visual stimulus for 1s?
    fixT = 0.5*fr # 0.5s just to note a new trial is starting
    respT = 2.5

    # define output pat
    filename = "data/{Subject ID}/{date}/{Subject ID}_mem".format(**info)

    'screen sections'
    fixation = visual.TextStim(win, text='+',pos=(0,0),color='black',units='pix',height=20)
    fixation_tstb = visual.ImageStim(win,  image='imgs/drop_black.png',ori=0, pos=[0, 0], size=(108/5,143/5), units='pix')
    fixation_tstgo = visual.ImageStim(win, image='imgs/drop_blue.png', ori=0, pos=[0, 0], size=(108/5,143/5), units='pix')
    fixation_rinse = visual.ImageStim(win, image='imgs/rinse.png', ori=0, pos=[0, 0], size=(175/5,143/5), units='pix')

    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # just to test the actual timing - display the seconds that go by
    timer_text = visual.TextStim(win, text='',
                                  font=f, pos=(-0.0, -0.15), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # load the images in order
    expVars = get_assoc_pairs_forMemTest(block)
    df = pd.DataFrame(expVars)  # [ 'TrialNum', 'CorrectAnswer','ImageLeft','ImageRight', 'flavor', 'flavorCode']
    CorrResp = df['CorrectAnswer'].tolist()
    ImRnames = df['ImageRight'].tolist()
    ImLnames = df['ImageLeft'].tolist()
    FlavorCodes = df['flavorCode'].tolist()

    imR = []
    for file in ImRnames:
        print(file)
        imR.append(visual.ImageStim(win=win, image=file, pos=(0.4, 0),size=(0.6, 0.9), units='norm'))

    imL = []
    for file in ImLnames:
        imL.append(visual.ImageStim(win=win, image=file, pos=(-0.4, 0), size=(0.6, 0.9), units='norm'))

    sz1 = imL[0].size
    sz2 = imR[0].size
    bordL = visual.Rect(win, size=sz1, units='norm', pos=(-0.4, 0), lineColor='white', lineWidth=2, fillColor='none')
    bordR = visual.Rect(win, size=sz2, units='norm', pos=(0.4, 0), lineColor='white', lineWidth=2, fillColor='none')

    # create a variable that will track trial timing infotmation
    globalClock = core.Clock()
    vol=0
    outputdf = pd.DataFrame({"vol": [vol],
                             "onset": [0.000],
                             "key": ['NaN'],
                             "trial_flavor": [0],
                             "imL": ['Nan'],
                             "imR": ['Nan'],
                             "imCorrect": ['NaN'],
                             "comment": ['start of scanning run']})

    # for i in range(-1 * MR_settings['skip'], 0):
    filename2 = "data/{Subject ID}/{date}/Triggers_run".format(**info) + str(block + 1) + ".csv"
    # use thistrial handler function to save the data
    trials = data.TrialHandler(trialList=list(flaves),nReps=1)
     #add trials to the experiment handler to store data
    thisExp = data.ExperimentHandler(
            name='flavors', version='1.0', #not needed, just handy
            extraInfo = info, #the info we created earlier
            dataFileName = filename ) # using our string with data/name_date
    thisExp.addLoop(trials)  # there could be other loops (like practice loop)

    # reset keyboard and if scanning - wait for first TR
    kb.clock.reset()
    kb.clearEvents()

    # mark first TR
    t = globalClock.getTime()
    outputdf.loc[len(outputdf)] = [1, t, TR_key, 'NaN', 'NaN', 'NaN', 'NaN', 'First TR']

    kb.clock.reset()

    # finally - strat looping oer trial and start experiment
    for i, corResp in enumerate(CorrResp):
        keys = []
        press_frame = []
        fl = FlavorCodes[i]
        fixation_tstb.setAutoDraw(True)
        for frames in range(13*fr): # 2S wait - 5staste -  3s chooseIm -  3s rinse
            if frames == 1.5*fr: # prepare for taste
                fixation_tstb.setAutoDraw(False)
                fixation_tstgo.setAutoDraw(True)
            elif frames == 2*fr: # deliver taste
                print('deliver taste')
                # arduino.write(str.encode(FlavorCodes[i]))  # LED turned on
            elif frames == 5*fr:
                fixation_tstgo.setAutoDraw(False)
                imL[i].setAutoDraw(True)
                imR[i].setAutoDraw(True)
                kb.clock.reset()
                kb.clearEvents()
                getResp = True
            elif 5*fr < frames < 10*fr:
                if getResp: # get response
                    keys = kb.getKeys(keyList=kl)
                if keys:
                    getResp = False
                    response = keys[0].name
                    decisionTime = keys[0].rt
                    if not press_frame:
                        press_frame = frames
                        t = globalClock.getTime()
                        outputdf.loc[len(outputdf)] = [vol, t, response, fl, ImLnames[i], ImRnames[i], corResp,'response']
                        kb.clearEvents()
                    elif (frames - press_frame) < 60:
                        # highlight border of chosen image
                        if response == kl[0]:
                            bordL.setAutoDraw(True)
                            imR[i].setAutoDraw(False)
                        elif response == kl[1]:
                            bordR.setAutoDraw(True)
                            imL[i].setAutoDraw(False)
                    elif (frames - press_frame) == 60:
                        bordL.setAutoDraw(False)
                        bordR.setAutoDraw(False)
                        imL[i].setAutoDraw(False)
                        imR[i].setAutoDraw(False)
                        fixation_tstb.setAutoDraw(False)
                        fixation_rinse.setAutoDraw(True)

            elif frames == 10*fr: #rinse
                imL[i].setAutoDraw(False)
                imR[i].setAutoDraw(False)
                fixation_rinse.setAutoDraw(True)
            elif frames == 10.5*fr:
                print('rinse')
                #arduino.write('0')


            # bail
            if event.getKeys(['escape']):
                core.quit()

            # listen to TRs
            keys_TR = kb.getKeys(keyList=TR_key)
            if keys_TR:
                vol += 1
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,TR_key,'NaN','NaN','NaN','NaN','TR']

            # if first frame - add note the trial started
            if frames == 1:
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol,t,'NaN',fl,ImLnames[i],ImRnames[i],corResp,'trail'+str(i) +'started']

            win.flip()

        # clear screen     and vars

        fixation_tstgo.setAutoDraw(False)
        fixation_rinse.setAutoDraw(False)
        win.flip()
        kb.clock.reset()
        kb.clearEvents()

    if demo == False:
        t = globalClock.getTime()
        outputdf.loc[len(outputdf)] = [vol, t, 'NaN',   'NaN', 'NaN',    ' NaN'  ,'NaN', 'End of scan']
        outputdf.to_csv(filename2, encoding='utf-8')

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
