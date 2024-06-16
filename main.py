from psychopy import visual, core, gui
from psychopy.hardware import keyboard
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
from tasks.flavorBlockTask import *
#from tasks.flavorCatBlockTask import *
#from tasks.Localizers import *

from utils import *


# define the -main- function:
# this is what is being run and it calls other functions from other scripts.
def main():

    " ***********HOUSE KEEPING***************"
    # create a dictionary with subject info
    info = {}
    info['Subject ID'] = 'test2'
    info['Experimenter Initials'] = 'sb'
    info['Scanning (0/1)'] = 1

    # create a GUI from the disctioary:
    # and present dialog to collect info
    dlg = gui.DlgFromDict(info, sortKeys=False)  # (and from psychopy import gui at top of script)
    if not dlg.OK:
        print('something not ok')
        core.quit()

    # add the date
    tdy = datetime.datetime.today()
    info['date'] = tdy.strftime("%b-%d-%Y")

    # output directory (if it doesnt exist - make one)
    if not os.path.exists("data/{Subject ID}".format(**info)):
        os.makedirs("data/{Subject ID}".format(**info))

    # create file tracking which tasks are done and which are not
    # initialize with zeros. if task was done, save the path to the result instead.
    filename = "data/{Subject ID}/tasks_{date}.csv".format(**info)

    if os.path.exists(filename):    # if the file already exists - read it
        taskTrack = pd.read_csv(filename)
    else: # if it doesn't create the dictionary and save the file
        taskTrack = pd.DataFrame.from_dict([info])
        taskTrack['demos'] = 0
        taskTrack['task'] = 0
        taskTrack.to_csv(filename, index=False, encoding='utf-8')

    "***********BEFORE SCAN***************"
    # 1. SCREEN AND KEYS
    # deefine window - anything we want to display will be through this variable
    win = visual.Window([1280, 800], fullscr=True, units='pix')
    # , units = 'norm'3840,2400
    # define keyboard: whatever ky is pressed will be stored in kb
    kb = keyboard.Keyboard()

    "TEST THE CONNECTION TO ARDUINO"
    #flavorBlockTest_test(info, win, kb, demo=True, block=0)

    Nblocks = 5
    for block in range(Nblocks):
        flavorBlockTest_test(info, win, kb,demo=False,block=block)
        betweenBlocks(info, win, kb)

    # this short function will call 2 flavors...
    #LocCat(info, win, kb, block=1)
    #FlavorCatBlockMemTest(info, win, kb, flaves='a', demo=False, block=1)
    #FlavorCatBlock(info,win,kb,flaves='a',demo=False,block=1)
    #flavorBlockTest_test(info, win, kb)

    # 2. FLAVOR PARAMETERS
    Ntastes = 7 # Separate taste: 2xSweeet, 2xBitter, 2xSour, 1xNeutral
    Nrepeat = 4 # per block..
    Nblocks = 5
    # overall 20 times per taste

    "***********IN MAGNET***************"
    "*************DEMOS*****************"
    '''
    if (taskTrack['demos'] == 0).bool():
        # get randomized order of flavors
        flaves_demo = get_flavor_order(Nflavors=2, Ntimes=1)
        # run a single block of this task for the demo - not scan
        flavorBlock(info, win, kb, flaves_demo, demo = 1,block=1)

    "*************TASK*****************"
    for block in range(Nblocks): # loop over the block
        # in each block get  randomized order of flavors:
        flaves = get_flavor_order(Ntastes,Nrepeat)
        # run the task (drink administration)
        flavorBlock(info, win, kb, flaves_demo, demo = 0,block=block)
        # after each block rate the flavor palatability
        rate_flavors(info, win, kb, block)
    '''

        # save output

    '''
    "***********AFTER SCAN***************"
    # also copy the results to the second day..
    # 1. color task confidence
    colorQuestion(info, win, kb)

    # 2. trivia memory task
    Qmemory(info, win, kb)    # Yaniv did it a week later.. and used free recall.

'''
###################################################################

if __name__ == "__main__":
    main()