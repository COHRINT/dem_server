#!/usr/bin/python2

#Given a hazard map and a list of goals, produce a policy pickle package

from MDPSolver import *
import sys
import csv
import numpy as np
import sys
import pickle, pprint

def solveGoal(hazMap, goal):
    ans = MDPSolver(modelName='HazmapModel', hazImg=hazMap, goal=goal);
    ans.solve()
    return ans

def loadGoals(fileName):
    src = open(fileName, 'rb')
    reader = csv.reader(src, delimiter = ',')
    goals = dict()
    for row in reader:
        print 'Got goal named ', row[0], ' at: ', row[1], ',', row[2] #Show in x,y
        goals[row[0]] = (int(row[2]), int(row[1])) #Save in row, col
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

    
    print 'Got scale:', hazPack['scale']
    return hazPack


    
def makePackage(hazPack, goals):
    #Save the policy pickle for further processing:
    #Include the goal, policy, hazmap, and scale factor
    package = {'scale' : hazPack['scale'],
               'hazmap' : hazPack['hazmap'],
               'src' : hazPack['src']}
    
    policies = dict()
    
    for goalID, goalLoc in goals.iteritems():
        print 'Goal:', goalID, ' ', goalLoc
        ans = solveGoal(hazPack['hazmap'], goalLoc)
        ans_clean = solveGoal(hazPack['hazmap_clean'], goalLoc)
        
        policyItem = {'goal' : goalLoc,
                      'actionMap' : ans.getActionMap(),
                      'actionMapClean' : ans_clean.getActionMap()}
        policies[goalID] = policyItem

    package['policies'] = policies

    output = open('polpack.pkl', 'wb')
    
    pickle.dump(package, output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'usage: ', sys.argv[0], ' <hazmap_scale.npy> <goals.csv>'
        sys.exit(0)
    hazPack= loadHazmap(sys.argv[1])
    goals = loadGoals(sys.argv[2])
    makePackage(hazPack, goals)
