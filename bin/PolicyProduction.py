#!/usr/bin/python2

#Given a hazard map and a list of goals, produce a policy pickle package

from MDPSolver import *
from mcts import *
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

def solveMCTS(hazMap, start, goal):
    ans = SolverMCTS(modelName='HazmapModel', hazImg=hazMap, start = 0, goal=goal);
    ans.testMCTS_Sim()
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

    
def makePackage(hazPack, goals):
    #Save the policy pickle for further processing:
    #Include the goal, policy, hazmap, and scale factor
    package = {'scale' : hazPack['scale'],
               'hazmap' : hazPack['hazmap'],
               'src' : hazPack['src']}
    
    policies = dict()

    #make an indexable goal list

    for goalID, rawGoalLoc in goals.iteritems(): #For goal in list
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
        #an_clean = solveMCTS(hazPack['hazmap_clean'], 0, goalLoc)
        actions = ans_clean.getActionMap()

        num_sims = 500
        print('Running MC Sims')
        hist_rewards = np.zeros((ans_clean.model.N,num_sims))
        action_list = []
        actual_action_list = []
        perf_list = []
        MC_results_list = np.zeros((ans_clean.model.N,num_sims))
        perf_R = np.zeros((ans_clean.model.N,2))
        results_list = []
        reward_list = np.zeros((ans_clean.model.N,2))
        for start in range(ans_clean.model.N):
            act_row = []
            actual_act_row = []
            perf_row = []
            for sim in range(num_sims):
                hist_rewards[start,sim], MC_actions, MC_results_list[start,sim] = ans_clean.MCSample(start,actions)
                act_row.append(MC_actions)
            action_list.append(act_row)

            actual_R, actual_actions, actual_results = ans_clean.ActualSample(start,actions)
            actual_act_row.append(actual_actions)
            actual_action_list.append(actual_act_row)
            reward_list[start,1] = actual_R
            results_list.append(actual_results)

            perf_actions, pr = ans_clean.perfSample(start, actions)
            perf_row.append(perf_actions)
            perf_list.append(perf_row)
            perf_R[start,1] = pr
            #ans_clean.getDist(start,goalLoc)
            

        policyItem = {'scaledGoal' : goalLoc,
                        'goal' : rawGoalLoc,
                        'actionMap' : ans.getActionMap(),
                        'actionMapClean' : ans_clean.getActionMap(),
                        'MCSims' : hist_rewards,
                        'MCActions' : action_list,
                        'MCResults' : MC_results_list,
                        'actualActions' : actual_action_list,
                        'actualR' : reward_list,
                        'actualResults' : results_list,
                        'perfR': perf_R,
                        'perfActions' : perf_list}
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
