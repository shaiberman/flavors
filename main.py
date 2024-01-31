from psychopy import visual, core, gui
from psychopy.hardware import keyboard
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
from tasks.flavorBlockTask import *
from utils import *

def main():

    # create a clock/timer to measure response times
    " ***********HOUSE KEEPING***************"
 
    info = {}  # a dictionary with subject info
    # present dialog to collect info
    info['Subject ID'] = 'test'
    info['Experimenter Initials'] = 'sb'
    info['Scanning (0/1)'] = 1
    dlg = gui.DlgFromDict(info, sortKeys=False)  # (and from psychopy import gui at top of script)
    if not dlg.OK:
        print('something not ok')
        core.quit()

    tdy = datetime.datetime.today()
    info['date'] = tdy.strftime("%b-%d-%Y")

    # create file tracking which tasks are done and which are not
    # initialize with zeros. if task was done, save the path to the result instead.
    filename = "data/{Subject ID}/tasks_{date}.csv".format(**info)
    # output directory
    if not os.path.exists("data/{Subject ID}".format(**info)):
        os.makedirs("data/{Subject ID}".format(**info))


    if os.path.exists(filename):
        taskTrack = pd.read_csv(filename)
    else:
        taskTrack = pd.DataFrame.from_dict([info])
        taskTrack['demos'] = 0
        taskTrack['task'] = 0
        taskTrack.to_csv(filename, index=False, encoding='utf-8')

    "***********BEFORE SCAN***************"
    # 1. SCREEN AND KEYS
    # i need to get monitor size. maybe check available monitors
    win = visual.Window([1280, 800], fullscr=True, units='pix')
    # define keyboard stuff
    kb = keyboard.Keyboard()

    "order the thing"
    Ntastes = 7 # Separate taste
    Nrepeat = 5 # per block.. overall 25 times per taste
    Nblocks = 5
    "timing"

    "***********IN MAGNET***************"
    "*************DEMOS*****************"

    flavorBlockTest(info, win, kb)

    if (taskTrack['demos'] == 0).bool():
        flaves_demo = get_flavor_order(Nflavors=2, Ntimes=1)
        flavorBlock(info, win, kb, flaves_demo, demo = 1,block=1)
        rate_flavors(info, win, kb,flaves_demo, block=1)

        print('demos while inside?')

    "***********IN MAGNET***************"
    "*************TASKS*****************"

    for block in range(0):#Nblocks):
        flaves = get_flavor_order(Ntastes,Nrepeat)
        flavorBlock(info, win, kb, flaves_demo, demo = 0,block=block)
        rate_flavors(info, win, kb, block)

        # 1. should we askk after every block for them to rate the flavors?
        # 2. should add rinse
        print('the flavors:')
        print(flaves)
        # 2.2 do the tasks.
        # do task
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