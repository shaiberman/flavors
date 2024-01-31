import os
import sys
import random
import pandas as pd
import numpy as np
import datetime
import shutil

_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expId = 'HRV'
foodStimFolder = '/static/foodstim60/'

tdy = datetime.datetime.today()
dt = tdy.strftime("%b-%d-%Y")


def get_task_results_exists(subjectId, resultsfilename):
    return os.path.exists(os.path.join(dataDir, expId, subjectId, subjectId + '_' + resultsfilename + '.csv'))


"""
Given name of current task and list of tasks, return the task that should be next
If task is final task, return 'thankyou' to route to thank you page
For example:, given tasks = ['auction','choicetask'] 
    print(get_next_task('auction', tasks))		# return 'choicetas
"""
def get_next_task(currentTask, taskOrder):
    for i in range(0, len(taskOrder)):
        task = taskOrder[i]
        if currentTask == task:
            if i < len(taskOrder) - 1:
                nextTask = taskOrder[i + 1]
                if nextTask == 'feedback' or nextTask == 'thankyou':
                    return nextTask
                elif 'instructions' in nextTask:
                    return 'instructions.' + nextTask
                else:
                    return 'tasks.' + nextTask
            else:
                return 'thankyou'
    return None


"""
WILLING TO PAY
"""
"""
There will be around 120 questions. maximum 200. 
so I want there to be around 50 food questions or 40?  
"""


'''general functions'''

def get_jitter():
    # jitter = [round(random.uniform(0.5, 2), 3) for i in range(1000)] # not in MRI
    jitter = [round(random.uniform(0.5, 2), 3) for i in range(1000)]
    return jitter

def get_wait():
    w = np.array([4, 6, 8, 10, 12, 14, 16])
    wait = np.repeat(w, 500)
    random.shuffle(wait)
    return wait

def get_pay_amounts():
    # w = np.array([4, 6, 8, 10, 12, 14, 16])
    w = np.array([1, 2, 3, 4, 5, 6, 7])
    wait = np.repeat(w, 500)
    random.shuffle(wait)
    return wait

def get_flavor_order(Nflavors, Ntimes):
    # w = np.array([4, 6, 8, 10, 12, 14, 16])
    w = np.array(range(1,Nflavors+1,1))
    flaves = np.repeat(w, Ntimes)
    random.shuffle(flaves)
    return flaves


'''for RATING'''

def get_trivia_all():
    questions = pd.read_csv(_thisDir + "/Kanga_TriviaList_goodQs.csv", usecols=['QuestionNum', 'Question', 'AnswerUse', 'IsFood'], encoding='unicode_escape')
    questions.columns = ['QuestionNum', 'Question', 'Answer','isFood']
    questions = questions.sample(frac=1).reset_index(drop=True) # randomize
    return questions

# get 100 questions. 30 food. hopeflly mostly unknown
def get_trivia(subjectId):
    questions_all = get_trivia_all()
    questions = get_unused_questions(subjectId, questions_all)  # will removed used questions from the pool

    # separate food and non food
    foodsQuestions = questions.loc[questions['isFood'] > 0, ['QuestionNum', 'Question', 'Answer']]
    genQuestions = questions.loc[questions['isFood'] == 0, ['QuestionNum', 'Question', 'Answer']]
    # shuffle the order
    foodsQuestions = foodsQuestions.sample(frac=1).reset_index(drop=True)
    genQuestions = genQuestions.sample(frac=1).reset_index(drop=True)
    # make sure there are enough of the food Qs
    frames = [ foodsQuestions[0:30] , genQuestions[0:70]]
    questions = pd.concat(frames)
    # randomize again
    questions = questions.sample(frac=1).reset_index(drop=True)

    return questions

def get_trivia_as_dicts(questions):
    keys = questions['Question'].values
    values = questions['Answer'].values
    dictionary1 = dict(zip(keys, values))
    keys = questions['Question'].values
    values = questions['QuestionNum'].values
    dictionary2 = dict(zip(keys, values))
    return dictionary1, dictionary2

# get 3 questions to practive on
def get_practice_trivia():
    questions = pd.read_csv(_thisDir + "/Kanga_PracticeQs.csv")
    questions.columns = ['QuestionNum', 'Question', 'Answer']
    questions = questions[0:3]
    questions = questions.to_dict('records')
    random.shuffle(questions)
    return questions

# gets the questions ans sets parameters for the rating scale
# this is now called no answer because we have separated the rating and the choice ask,
# thus no answer is necessary for this stage.
def get_Qratingtask_expVariables_noanswer(subjectId):
    # overall there are about 460, out of ~70 are food related.
    # this should gets 200 Qs, 30 of which are food Qs.
    # I should put in place something for the second time this is done.
    questions = get_trivia(subjectId)
    questions.to_dict('records')
    # how many Qs do i want?
    trivia_dict, trivia_qnum_dict = get_trivia_as_dicts(questions)
    qs = questions['Question'].values
    expVariables = []
    rs_min = 0
    rs_max = 100
    rs_tickIncrement = 25
    rs_increment = 1
    rs_labelNames = ["0", "25", "50", "75", "100"]
    for q in qs:
        trial = {}
        trial['TrialType'] = 'RateQuestion'
        trial['Question'] = q
        answer = trivia_dict[q]
        trial['Answer'] = answer
        qnum = trivia_qnum_dict[q]
        trial['QuestionNum'] = int(qnum)
        trial['rs_min'] = int(rs_min)
        trial['rs_max'] = int(rs_max)
        trial['rs_tickIncrement'] = rs_tickIncrement
        trial['rs_increment'] = rs_increment
        trial['rs_labelNames'] = rs_labelNames
        expVariables.append(trial)
    return expVariables


''' for the second time around'''

def get_questions_used_in_rating_task_day1(subjectId):
    datafile = os.path.join(dataDir, expId, 'day1rating', subjectId + '_QRatings_day1.csv')
    if os.path.exists(datafile):
        df = pd.read_csv(datafile)
        questions = df['Question'].values.tolist()
        return questions
    print("File not found")
    return []

def get_unused_questions(subjectId,questions):
    old_questions = get_questions_used_in_rating_task_day1(subjectId)
    unused_questions = questions.loc[~questions['Question'].isin(old_questions)]
    unused_questions = unused_questions.sample(frac=1).reset_index(drop=True)
    return unused_questions

'''WTP'''
# only use the 80 top rated question that were unknown!
def get_questions_used_in_rating_task(subjectId):
    datafile = os.path.join(dataDir, subjectId, 'wtp_rate_' + subjectId +'_'+ dt + '.csv')
    if os.path.exists(datafile):
        df = pd.read_csv(datafile)
        if not 'Know' in df.keys():
            print('SOMETHING WRONG WITH TRIVIA RATING FILE')
        # collect only Qs whose answer they don't know:
        df = df.loc[df['Know'] == 0]

        # collect the top 66 questions -
        ratings = df['rating'].to_numpy(dtype=float)
        q = 100 * (len(ratings) - 60) / len(ratings) # the percentile that will give us 60 of however many questins were unknown
        #q = 100 * (len(ratings) - 4) / len(ratings)
        p = np.percentile(ratings, q) # the rating value of this percentile
        df = df.loc[ratings > p] # all Qs above that number
        questions = df['Question'].values.tolist()
        return questions
    else:
        print("This File not found:"+datafile)
        return []


def get_wtp_trivia(subjectId):
    # questions = get_trivia()
    questions = get_trivia_all()
    # get the 60 top-rates questions (whose answer was unknown)
    top_questions = get_questions_used_in_rating_task(subjectId)
    questions = questions.loc[questions['Question'].isin(top_questions)]

    questions = questions.to_dict('records')
    random.shuffle(questions) # unnecessary i believe
    return questions


def get_comprehensiontestinfo_WTP() -> object:
    info = pd.read_csv(_thisDir + '/ComprehensionTestWTP.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            options.append(str(i))
        new_info.append({q: options})
    return new_info

def get_wtp_viewedQs(subjectId):
    subDir = os.path.join(_thisDir, '..', 'data', subjectId)
    file_path = os.path.join(subDir, 'wtp_' +subjectId + '_' + dt + '.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'Choice' in df.columns:
            Qs = df.loc[df['Choice'] == '2', 't'].Question
            As = df.loc[df['Choice'] == '2', 't'].Answer
        else:
            Qs = []
            As = []
    return Qs, As

"""
Get total about subject indicated they were willing to pay for questions
Returns amount in cents
"""
def get_wtp_pay_amount(expId, subjectId):
    subDir = os.path.join(_thisDir, '..', 'data', subjectId)
    file_path = os.path.join(subDir, 'wtp_' + subjectId + '_' + dt + '.csv')
    totalAmount = 0
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'Choice' in df.columns:
            payTrialAmounts = df.loc[df['Choice'] == 't', '2'].Values
            totalAmount = np.sum(payTrialAmounts)
        else:
            totalAmount = 0
    return totalAmount

"""
FOOD RATING AND FOOD CHOICES!
"""


def organize_stim60dir(subjectId):
    # all stimuli
    all_stimuli = []
    for stimulusFile in os.listdir(os.path.join(_parentDir, 'static','AllFoodStim')):
        if stimulusFile.endswith('jpg'):
            all_stimuli.append(stimulusFile[:-4])

    # check if they've already done this
    datafile = os.path.join(dataDir, 'day1rating', subjectId + '_FoodRatings_day1.csv')
    print(datafile)
    # if they hav
    if os.path.exists(datafile):
        # take random 30 from her eand random 30 from main that are NOT here
        df = pd.read_csv(datafile, delimiter=',', encoding="utf-8-sig")
        stim_used=df.stimulus1.values.tolist()
        stim_notused = np.setdiff1d(all_stimuli, stim_used)
        stim_notused.tolist()

        stim_used_move = random.sample(list(stim_used),30)# stim_used.sample(frac=0.5).reset_index(drop=True) #take 30 of 60 items
        stim_notused_move = random.sample(list(stim_notused),30)
        stim = stim_used_move + stim_notused_move

        # print(all_stimuli)

        print('copying 30 old and 30 new stimuli to stim folder')
    else:
        # take 60 random from there
        stim = random.sample(all_stimuli,60)
        print('copying 60 random images to stim folder')
    # now move the stimuli to the stim60 folder!
    for st in stim:
        stim_path= os.path.join(_parentDir, 'static','AllFoodStim',st+'.jpg')
        stim_path_new = os.path.join(_parentDir,'static','foodstim60',st+'.jpg')
        shutil.copyfile(stim_path ,stim_path_new)

    return []

def clear_stim_folder():
    for stimulusFile in os.listdir(os.path.join(_parentDir,'static','foodstim60')):
        if stimulusFile.endswith('jpg'):
            os.remove(os.path.join(_parentDir,'static','foodstim60',stimulusFile))
    return []

#Returns a list of all stimuli in the stim folder (assuming all the .bmp files are stimulus images)
def get_stimuli(folder, prepend, fileextension):
    # get array of stimuli from the directory name stim
    stimuli = []
    for stimulusFile in os.listdir(_parentDir + folder):
        if stimulusFile.endswith(fileextension):
            stimuli.append(prepend + stimulusFile[:-4])
    return stimuli


"""
Pair up lists of stimuli without taking bids into account
"""


def get_two_stimuli_lists_without_bids(folder, prepend, fileextension):
    stimuli1 = get_stimuli(folder, prepend, fileextension)
    random.shuffle(stimuli1)
    stimuli2 = get_stimuli(folder, prepend, fileextension)
    random.shuffle(stimuli2)
    shamBids = []
    for i in range(0, len(stimuli1)):
        shamBids.append(-1)
        if stimuli1[i] == stimuli2[i]:
            newIndex = random.randint(0, len(stimuli1) - 1)
            while newIndex == i or stimuli1[newIndex] == stimuli2[newIndex]:
                newIndex = random.randint(0, len(stimuli1) - 1)
            oldStimulus = stimuli2[i]
            stimuli2[i] = stimuli2[newIndex]
            stimuli2[newIndex] = oldStimulus
    return [stimuli1, shamBids, stimuli2, shamBids]


"""
Get lists of two stimuli for choice task
Stimuli are first rank ordered by bid
pairDiff determines the various differences between the indices of each pair
For each pair in pairDiff, there are unique pairings for each stimulus
Since there are 7 elements in pairDiff and 60 stimuli, there are 7 * (60/2) = 210 pairings in total
The order of the pairings is randomized so that on one trial, the first stimulus may be 2 indices apart from the second stimulus
    and then on the next trial, the first stimulus may be 10 indices apart from the second stimulus
The order of the stimuli within pairings is also randomized so that the stimulus with the higher bid 
    is randomly put on the left or the right
The array returned contains lists of the stimulus names and their respective bids
nTrials is an optional argument 
"""


def get_two_stimuli_lists(stimBidDF, folder, prepend, fileextension, nTrials):
    result = stimBidDF.sort_values("bid")
    result = result.reset_index(drop=True)

    # for LUT v1, we just want 110 trials with enough spread for delta value
    # there are 30 trials per pairDiff;
    # to get 110 trials, we can randomly select 15 trials per pairDiff --> 105 trials
    # we can select another 5 trials from pairDiff == 1

    # for LUT v2, we want 180 trials
    if len(stimBidDF) == 60:
        #pairDiff = [1, 2, 6, 10, 15, 30]
        pairDiff = [1, 2, 3, 6, 10, 15, 30]
    elif len(stimBidDF) == 80:
        if nTrials == 280:
            pairDiff = [1, 2, 5, 8, 10, 20, 40]
        else:
            pairDiff = [1, 2, 4, 5, 8, 10, 20, 40]
    else:
        print('NOT ENOUGH PAIRS FOR FOOD!')

    stimuli = get_stimuli(folder, prepend, fileextension)
    nStim = len(stimuli)

    shuffledDf = pd.DataFrame()
    for diff in pairDiff:
        pairingIndices = get_pairingIndices([diff], nStim)
        df = get_stimulus_pairings(result, pairingIndices)  # should have 30 trials
        df = df.sample(frac=1)
        shuffledDf = pd.concat([shuffledDf, df])

    """
    shuffledDf = pd.DataFrame()
    for diff in pairDiff:
        pairingIndices = get_pairingIndices([diff], nStim)
        df = get_stimulus_pairings(result, pairingIndices)  # should have 30 trials
        if diff in [1, 3, 6, 10, 15]:
            pairDf = df.sample(frac=16 / 30.0)
        else:
            pairDf = df.sample(frac=0.5)
        shuffledDf = pd.concat([shuffledDf, pairDf])
    """

    shuffledDf = shuffledDf.sample(frac=1)
    stim1Names = shuffledDf['stimulus1'].values
    stim2Names = shuffledDf['stimulus2'].values
    stim1Bids = shuffledDf['stim1Bid'].values
    stim2Bids = shuffledDf['stim2Bid'].values
    return [stim1Names, stim1Bids, stim2Names, stim2Bids]


"""
Helper method used in get_two_stimuli_lists to get list of pairings of stimuli
"""


def get_pairingIndices(pairDiff, nStim):
    pairingIndices = []
    for x in pairDiff:
        stimUsed = resetStimUsed(
            nStim)  # keep track of whether stimulus has been used in a pairing for this difference already
        for i in range(0, nStim - x):
            if stimUsed[i] == False:
                pairingIndices.append([i, i + x])
                stimUsed[i] = True
                stimUsed[i + x] = True
    return pairingIndices


"""
Helper method used in get_two_stimuli_lists to get dictionary of pairings of stimuli and their rank bid differences
"""


def get_stimulus_pairings(result, pairingIndices):
    dfList = []
    for pair in pairingIndices:
        trialStim = {}
        # shuffles indices within pairings
        stim1Index = random.randint(0, 1)
        if stim1Index == 0:
            stim2Index = 1
        else:
            stim2Index = 0
        stimulus1 = result.loc[pair[stim1Index]]['stimulus']
        stimulus2 = result.loc[pair[stim2Index]]['stimulus']
        stim1Bid = float(result.loc[pair[stim1Index]]['bid'])
        stim2Bid = float(result.loc[pair[stim2Index]]['bid'])

        trialStim['bidRankDifference'] = pair[1] - pair[0]
        trialStim['stimulus1'] = stimulus1
        trialStim['stimulus2'] = stimulus2
        trialStim['stim1Bid'] = stim1Bid
        trialStim['stim2Bid'] = stim2Bid

        dfList.append(trialStim)
    df = pd.DataFrame(dfList)
    return df


"""
Helper method for get_two_stimuli_lists
Returns a dictionary with keys from 0 to nStim-1, with each value as false
"""


def resetStimUsed(nStim):
    stimUsed = {}
    for i in range(0, nStim):
        stimUsed[i] = False
    return stimUsed


"""
Returns a dictionary of the stimuli as keys and their bids as values
csv_name is the location + name of the csv file where the bids are located
The csv must have the stimulus name in a column with the heading "stimulus1"
    the bid must be in a column with the heading "rating"
"""


def get_bid_responses(csv_name):
    '''
    from a csv file generated by the auction task, generate a dictionary of the stimuli and the participant's bids
    '''
    df = pd.read_csv(csv_name)
    #print(csv_name)
    #print(df)
    stim = df.loc[:, 'stimulus1']
    bids = df.loc[:, 'rating']
    stimBidDF = pd.concat([bids, stim], axis=1)
    stimBidDF = stimBidDF.rename(index=str, columns={"rating": "bid", "stimulus1": "stimulus"})
    return stimBidDF


"""
Creates list of dictionaries where each dictionary holds the variables for one trial
Args:
    question: question to be displayed above image
    leftRatingText: text to display below left most part of rating scale
    rightRatingText: text to display below right most part of rating scale
    *The last few params correspond to the variables used to construct the rating scale
    rs_min: minimum value on rating scale
    rs_max: maximum value on rating scale
    rs_tickIncrement: numerical difference between the ratings that are labeled
    rs_increment: numerical difference between consecutive ratings
    rs_labelNames: array of labels for each tick
"""


def get_ratingtask_expVariables(expId, subjectId, demo, question, leftRatingText, middleRatingText, rightRatingText,
                                rs_min, rs_max, rs_tickIncrement, rs_increment, rs_labelNames):
    if demo == True:
        stimuli = get_stimuli(foodStimFolder + 'demo/', '', '.jpg')
    else:
        stimuli = get_stimuli(foodStimFolder, '', '.jpg')
    random.shuffle(stimuli)

    expVariables = []  # array of dictionaries

    for i in range(0, len(stimuli)):
        expVariables.append({'stimulus': stimuli[i], 'fullStimName': stimuli[i] + '.jpg', 'question': question,
                             'leftRatingText': leftRatingText, 'middleRatingText': middleRatingText,
                             'rightRatingText': rightRatingText, 'rs_min': rs_min, 'rs_max': rs_max,
                             'rs_tickIncrement': rs_tickIncrement, 'rs_increment': rs_increment,
                             'rs_labelNames': rs_labelNames})
    return expVariables

""" COLOR"""
def get_color_questionnaire():
    info = pd.read_csv(_thisDir + '/' + 'ColorTaskQuestions.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

# name: COVID, Fires, General, Storms
def get_questionnaire(name):
    info = pd.read_csv(_thisDir + '/' + 'AnxietyQuestions_' + name + '.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_demographicq():
    info = pd.read_csv(_thisDir + '/DemographicQuestions.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_hungerq():
    info = pd.read_csv(_thisDir + '/HungerQuestions.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_EATq():
    info = pd.read_csv(_thisDir + '/EAT26.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_MEQ():
    info = pd.read_csv(_thisDir + '/MEQ.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_IEQ():
    info = pd.read_csv(_thisDir + '/IEQ.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            if (type(i) == str) or (type(i) == bytes):  # remove nan values
                options.append(i)
        new_info.append({q: options})
    return new_info

def get_comprehensiontestinfo():
    info = pd.read_csv(_thisDir + '/ComprehensionTest.csv', delimiter=',', encoding="utf-8-sig")
    questions = info['Question']
    info = info.set_index('Question')
    new_info = []
    for j in range(0, len(questions)):
        q = questions[j]
        tmp = info.loc[q].values
        options = []
        for i in tmp:
            options.append(str(i))
        new_info.append({q: options})
    return new_info


"""
Checks request.args has assignmentId, hitId, turkSubmitTo, workerId, live - all but live is passed by MTurk
live refers to whether HIT is live or in sandbox
"""


def contains_necessary_args(args):
    if 'workerId' in args and 'assignmentId' in args and 'hitId' in args:
        return True
    else:
        return False


"""
Retrieve necessary args: assignmentId, hitId, turkSubmitTo, workerId, live
"""


def get_necessary_args(args):
    workerId = args.get('workerId')
    assignmentId = args.get('assignmentId')
    hitId = args.get('hitId')
    turkSubmitTo = 'https://www.mturk.com'
    live = True
    return [workerId, assignmentId, hitId, turkSubmitTo, live]


def make_pairs_for_demo(foodStimFolder):
    [stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(
        foodStimFolder + '/demo/', '', '.jpg')
    expVariables = []  # array of dictionaries
    deltas = []
    for i in range(len(stim1Bids)):
        deltas.append(stim2Bids[i] - stim1Bids[i])

    for i in range(len(stim1Bids)):
        expVariables.append({"stimulus1": stim1Names[i], "stimulus2": stim2Names[i],
                             "stim1Bid": stim1Bids[i], "stim2Bid": stim2Bids[i],
                             "delta": deltas[i],
                             "fullStim1Name": stim1Names[i] + ".jpg", "fullStim2Name": stim2Names[i] + ".jpg"})

    return expVariables


def make_pairs_for_exp(resfile2):
    # make_pairs_not_for_demo
    stim1Bids = [];
    stim2Bids = [];
    stimBidDict = get_bid_responses(resfile2)
    [stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder, '', '.jpg', 280)
    expVariables = []  # array of dictionaries
    deltas = []
    for i in range(len(stim1Bids)):
        deltas.append(stim2Bids[i] - stim1Bids[i])

    for i in range(len(stim1Bids)):
        expVariables.append(
            {"stimulus1": stim1Names[i], "stimulus2": stim2Names[i], "stim1Bid": stim1Bids[i],
             "stim2Bid": stim2Bids[i], "delta": deltas[i], "fullStim1Name": stim1Names[i] + ".jpg",
             "fullStim2Name": stim2Names[i] + ".jpg"})

    return expVariables


