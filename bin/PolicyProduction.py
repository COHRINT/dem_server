#lID!/usr/bin/python2

#Given a hazard map and a list of goals, produce a policy pickle package

from MDPSolver import *
import sys
import csv
import numpy as np
import sys
import pickle, pprint
import pdb

def solveGoal(hazMap, goal):
    ans = MDPSolver(modelName='HazmapModel', hazImg=hazMap, goal=goal);
    ans.solve()
    return ans

def loadGoals(fileName):
    src = open(fileName, 'rb')
    reader = csv.reader(src, delimiter = ',')
    goals = dict()
    for row in reader:
        print('Got goal named ', row[0], ' at (row,col): ', row[1], ',', row[2])
        goals[row[0]] = (int(row[1]), int(row[2])) #Save in row, col
    return goals

def loadHazmap(fileName):
    pfile = open(fileName, 'rb')
    hazPack = pickle.load(pfile)
    

    '''
    hazMap = np.load(fileName)
    scale_splits = fileName.split('_')
    scale_file = scale_splits[1].split('.')

    scale = '%s.%s' % (scale_file[0], scale_file[1])
    '''

    
    print('Got scale:', hazPack['scale'])
    return hazPack

def outcomeAssessment(samples, R_inf):
    L_samples=np.unique(np.where(samples<R_inf))
    U_samples=np.unique(np.where(samples>R_inf))
    samples=list(samples)
    LPM=sum([float(x*samples.count(x))/float(len(samples)) for x in L_samples])
    UPM=sum([float(x*samples.count(x))/float(len(samples)) for x in U_samples])
    xO=(float(2)/(1+np.exp(-np.log(float(UPM)/float(LPM)))))-1


    
def makePackage(hazPack, goals):
    #Save the policy pickle for further processing:
    #Include the goal, policy, hazmap, and scale factor
    package = {'scale' : hazPack['scale'],
               'hazmap' : hazPack['hazmap'],
               'src' : hazPack['src']}
    
    policies = dict()
    
    for goalID, rawGoalLoc in goals.iteritems():
    #  goalID=list(goals)[0]
    #  rawGoalLoc=goals[goalID]

        print('Goal:', goalID, ' ', rawGoalLoc)

        #Scale the goals according to the scale in the hazPack:

        goalLoc = (int(rawGoalLoc[0] * hazPack['scale']), int(rawGoalLoc[1] * hazPack['scale']))
        print('Goal (row, col):', goalID, ' Scaled:', goalLoc)
        
        print('Solving hazmap')
        ans = solveGoal(hazPack['hazmap'], goalLoc)
        print('Solving hazmap clean')
        ans_clean = solveGoal(hazPack['hazmap_clean'], goalLoc)
        actions = ans_clean.getActionMap()
        num_sims = 100
        print('Running MC Sims')
        hist_rewards = np.zeros((ans_clean.model.N,num_sims))
        for start in range(ans_clean.model.N):
            for sim in range(num_sims):
                hist_rewards[start,sim] = ans_clean.MCSample(start,actions)
        
        
        policyItem = {'scaledGoal' : goalLoc,
                        'goal' : rawGoalLoc,
                        'actionMap' : ans.getActionMap(),
                        'actionMapClean' : ans_clean.getActionMap(),
                        'MCSims' : hist_rewards}
        policies[goalID] = policyItem

    package['policies'] = policies

    output = open('polpack.pkl', 'wb')
    
    pickle.dump(package, output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: ', sys.argv[0], ' <hazpack.pkl> <goals.csv>')
        sys.exit(0)
    hazPack= loadHazmap(sys.argv[1])
    goals = loadGoals(sys.argv[2])
    makePackage(hazPack, goals)
