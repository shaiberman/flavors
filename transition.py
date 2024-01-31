from psychopy import visual, event, core, data, gui
from psychopy.hardware import keyboard

from dmstudies.utils import * # this used to be "from utils import *"

f = 'Calibri'
kl = ['space', '1']


def first_slide(win,kb):
    kb.clock.reset()
    kb.clearEvents()
    win.color = 'white'
    txt = visual.TextStim(win,text='Before entering the scanner you will perform 2 rating tasks. \n\n'
                                   'You will judge trivia questions and food item, \nbased on your own opinions.\n\n\n '
                                   'Click anywhere to see instruction for the first task..',
                                 font=f,pos=(0.0,0.0), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.08, antialias=True, bold=True, italic=False)
    # make sure they get instruction before starting
    mouse = event.Mouse()
    while not mouse.getPressed()[0]:
        txt.setAutoDraw(True)
        win.flip()
    txt.setAutoDraw(False)
    win.flip()
    mouse.clickReset()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.5)

def trans(win,kb,demo):
    kb.clock.reset()
    kb.clearEvents()
    win.color = 'white'
    if demo==True:
        trans_text = visual.TextStim(win,text='You will now be introduced to a new task. \n\n Press your index finger to read the instructions and go through some guided practice',
                                 font=f,pos=(0.0,0.4), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.07, antialias=True, bold=False, italic=False)
    else:
        trans_text = visual.TextStim(win,
                                     text='You will now begin a new block in a new task. \n\n Press your index finger to start',
                                     font=f,pos=(0.0, 0.4), depth=0, rgb=None, color='black',
                                     colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                     ori=0.0, height=0.07, antialias=True, bold=False, italic=False)
    keys = kb.getKeys(keyList=kl)
    while not keys:
        keys = kb.getKeys(keyList=kl)
        trans_text.setAutoDraw(True)
        win.flip()
    trans_text.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.5)  # a typical mouse-click takes ~100ms, 6-9 frames of the mouse being down


def trans_demos(win,kb):
    kb.clock.reset()
    kb.clearEvents()
    win.color = 'white'
    trans_text = visual.TextStim(win,text='You will now be introduced to several tasks, and go through some guided practice. \n\n '\
                                          'Press your index finger to start with the first task',
                                 font=f,pos=(0.0,0.4), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.07, antialias=True, bold=False, italic=False)

    keys = kb.getKeys(keyList=kl)
    while not keys:
        keys = kb.getKeys(keyList=kl)
        trans_text.setAutoDraw(True)
        win.flip()
    trans_text.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.5)  # a typical mouse-click takes ~100ms, 6-9 frames of the mouse being down



def trans_tasks(win,kb):
    kb.clock.reset()
    kb.clearEvents()
    win.color = 'white'
    trans_text = visual.TextStim(win,text='You will now perform the full tasks.\n\n'
                                          'The 3 tasks will alternate in 3 blocks.\n\n '
                                          'You will have a chance to take a short break between each block. \n\n '\
                                          'Press you index finger to start with the first task',
                                 font=f,pos=(0.0,0.3), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.07, antialias=True, bold=True, italic=False)

    keys = kb.getKeys(keyList=kl)
    while not keys:
        keys = kb.getKeys(keyList=kl)
        trans_text.setAutoDraw(True)
        win.flip()
    trans_text.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.5)  # a typical mouse-click takes ~100ms, 6-9 frames of the mouse being down

def trans_magnet(win,kb):
    kb.clock.reset()
    kb.clearEvents()
    win.color = 'white'

    trans_text = visual.TextStim(win,text='Thank you!\n\n Your next tasks will be performed in the scanner.\n\n Please press ESC',
                                 font=f,pos=(0.0,0.4), depth=0, rgb=None, color='black',
                                 colorSpace='rgb', opacity=1.0, contrast=1.0, units='norm', wrapWidth=1.8,
                                 ori=0.0, height=0.08, antialias=True, bold=True, italic=False)

    keys = kb.getKeys(keyList='escape')
    while not keys:
        keys = kb.getKeys(keyList='escape')
        trans_text.setAutoDraw(True)
        win.flip()
    trans_text.setAutoDraw(False)
    win.flip()
    kb.clock.reset()
    kb.clearEvents()
    core.wait(.5)  # a typical mouse-click takes ~100ms, 6-9 frames of the mouse being down
    core.quit()
