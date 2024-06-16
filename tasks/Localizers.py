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
'''
The localizer uses a miniblock design :
eight stimuli of the same category are presented in each 4 second trial (500 ms/image). 
For each 5 minute run, a novel stimulus sequence is generated, 
this  counterbalances the ordering of five stimulus domains  and a blank baseline condition. 
They use (characters, bodies, faces, places, and objects), we might only use faces bodies and places  
 For each stimulus domain, there are two associated image categories 
 They  are presented in alternation over the course of a run but never intermixed within a trial:
 
Bodies: body vs limb
Faces: adult vs child
Places: house vs corridor 

There's also a task! chosen from:
1-back - detect back-to-back image repetition
2-back - detect image repetition with an intervening stimulus
Oddball - detect replacement of a stimulus with scrambled image
 '''



f = 'Calibri'

'''
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
############  TASK   ###########
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def LocCat(info,win,kb,block):
    # CHANGEABLE    PARAMETERS
    countDown = 12 # pre - experiment countdown(secs)
    stimSize = 768 # size to display images in pixels
    fixColor = (255, 0, 0) # fixation marker color (red?)
    textColor = 255 # instruction text color(black)
    waitDur = 1 # secs to wait for response(must be < 2 and a multiple of .5)

    # (info, win, kb, demo)    # present instructions:
    win.color=[0.5,0.5,0.5]    # change screen baclground to grey
    win.mouseVisible = False   # hide cursor

    # info about the trials timing:
    fr = 60 # frame rate (how many times a second is the screen represhed
    ''' RESPONSE KEY'''
    TR_key='5' # if we are scanning - the MRI TR will appear as a 5-key press.
    if info['Scanning (0/1)']==0:
        kl = ['space'] # allowed keys
    else:
        kl = ['1']

    '''SCREEN AND STIMULI'''
    load_screen = visual.TextStim(win, text='Loading stimuli...',
                                  font=f, pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)
    load_screen.setAutoDraw(True)
    win.flip()
    scriptFile = 'loc/script_fLoc_1back_run'+str(block)+'.csv'
    Trials = pd.read_csv(scriptFile)
    numTrials =len(Trials)
    onsets=Trials['onset'].tolist()
    viewTime = onsets[1]
    cat = Trials['cond'].tolist()
    catDirs = ['blank','body', 'limb', 'adult', 'child', 'corridor', 'house']

    stim = Trials['img'].tolist()
    images = []
    for i,file in enumerate(stim):
        if file == 'blank':
            images.append(visual.TextStim(win, text='+',font=f,pos=(0, 0), depth=0, rgb=None, color=[0.5,0.5,0.5])) # invisivle fixation..?
        else:
            dd = catDirs[cat[i]]
            images.append(visual.ImageStim(win=win, image='loc/'+dd+'/'+file, pos=(0, 0), size=stimSize, units='pix'))

    load_screen.setAutoDraw(False)

    fixation = visual.TextStim(win, text='+',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='red',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    wait_screen = visual.TextStim(win, text='Waiting for scanner...',
                                  font=f,pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)
    instruction = visual.TextStim(win, text='Fixate. Press a button when an image repeats on sequential trials.\nPress button to continue.',
                                  font=f, pos=(0, 0), depth=0, rgb=None, color='black',
                                  colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                  ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    '''INSTRUCTIONS AND TRIGGER CHECKS'''
    keys_start =  kb.getKeys(keyList=kl)
    while not keys_start:
        keys_start = kb.getKeys(keyList=kl)
        instruction.setAutoDraw(True)
        win.flip()
    instruction.setAutoDraw(False)
    win.flip()

    # reset keyboard
    kb.clock.reset()
    kb.clearEvents()

    '''SAVE FILES'''
    # create a variable that will track trial timing infotmation
    globalClock = core.Clock()
    vol=0
    outputdf = pd.DataFrame({"vol": [vol],
                             "onset": [0.000],
                             "key": ['NaN'],
                             "Im": ['NaN'],
                             "comment": ['start of scanning run']})

    # for i in range(-1 * MR_settings['skip'], 0):
    filename = "data/{Subject ID}/{date}/Triggers_run".format(**info) + str(block + 1) + ".csv"
    filename1 = "data/{Subject ID}_{date}_Triggers_run2".format(**info) + str(block + 1)

    trials = data.TrialHandler(trialList=list(images),nReps=1)
    thisExp = data.ExperimentHandler(
            name='cats', version='1.0', #not needed, just handy
            extraInfo = info, #the info we created earlier
            dataFileName = filename1 ) # using our string with data/name_date
    thisExp.addLoop(trials)  # there could be other loops (like practice loop)

    '''INIT PARAMS'''
    # reset keyboard and if scanning - wait for first TR
    kb.clock.reset()
    kb.clearEvents()
    # waitForScanner - allow 2 minutes of waiting...
    # mark first TR
    t = globalClock.getTime()
    # waitForScanner - allow 2 minutes of waiting...
    wait_screen.setAutoDraw(True)
    win.flip()
    kb.waitKeys(maxWait=120, keyList=[TR_key], waitRelease=True, clear=True)
    wait_screen.setAutoDraw(False)
    outputdf.loc[len(outputdf)] = [1, t, TR_key, 'NaN', 'First TR']
    kb.clock.reset()

    '''PRE EXP COUNTDOWN'''
    timer_text = visual.TextStim(win, text=countDown.__str__(),
                                 font=f, pos=(0, 0), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.1, antialias=True, bold=True, italic=False)

    # display     countdown    numbers
    secs = 12
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
    fixation.setAutoDraw(True)  # trial onset fixation

    '''MAIN LOOP'''
    # finally - strat looping oer trial and start experiment
    for i, im in enumerate(images):
        t = globalClock.getTime()
        outputdf.loc[len(outputdf)] = [vol, t, TR_key, stim[i], 'trial started ']

        for frames in range(int(60/4)): #250ms
            im.draw()
            fixation.draw()  # trial onset fixation
            win.flip()

            # listen to TRs
            keys_TR = kb.getKeys(keyList=TR_key)
            if keys_TR:
                vol += 1
                t = globalClock.getTime()
                outputdf.loc[len(outputdf)] = [vol, t, TR_key, 'NaN', 'TR']

        # bail
        if event.getKeys(['escape']):
            core.quit()

        # clear screen     and vars
        im.setAutoDraw(False)
        win.flip()
        kb.clock.reset()
        kb.clearEvents()

    fixation.setAutoDraw(False)
    t = globalClock.getTime()
    outputdf.loc[len(outputdf)] = [vol, t, 'NaN','NaN', 'End of scan']
    outputdf.to_csv(filename, encoding='utf-8')

    win.mouseVisible = True
    win.flip()
    kb.clock.reset()
    kb.clearEvents()

    return filename + ".csv"
