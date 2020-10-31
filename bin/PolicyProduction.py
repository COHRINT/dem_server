#!/usr/bin/python2

#Given a hazard map and a list of goals, produce a policy pickle package

from MDPSolver import *
from mcts import *
import floyd as floyd
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

    
def makePackage(hazPack, goals):
    #Save the policy pickle for further processing:
    #Include the goal, policy, hazmap, and scale factor
    package = {'scale' : hazPack['scale'],
               'hazmap' : hazPack['hazmap'],
               'src' : hazPack['src']}
    
    policies = dict()

    #make an indexable goal list
    goalList = list(goals.iteritems())

    for i in range(0,len(goalList)):
        goalID = goalList[i][0]
        rawGoalLoc = goals[goalID]
        startID = goalList[i-1][0]
        rawStartLoc = goals[startID]

    #for goalID, rawGoalLoc in goals.iteritems(): #For goal in list
    #  goalID=list(goals)[0]
    #  rawGoalLoc=goals[goalID]
        print('Solving Floyd Warshall')
        if i == 0:
            costmap, nextPlace = floyd.floyds(hazPack['hazmap_clean'])
            np.save('floydWarshallCosts', costmap)
        else:
            costmap = np.load('floydWarshallCosts.npy')
        #print costmap[0][0][0][0], costmap[9][2][2][19]
        print('Goal:', goalID, ' ', rawGoalLoc)

        #Scale the goals according to the scale in the hazPack:

        goalLoc = (int(rawGoalLoc[0] * hazPack['scale']), int(rawGoalLoc[1] * hazPack['scale']))
        startLoc = (int(rawStartLoc[0] * hazPack['scale']), int(rawStartLoc[1] * hazPack['scale']))
        print('Goal (row, col):', goalID, ' Scaled:', goalLoc)

        
        #print('Solving hazmap')  
        #ans = solveGoal(hazPack['hazmap'], goalLoc)
        print('Solving hazmap clean')
        ans_clean = solveGoal(hazPack['hazmap_clean'], goalLoc)
        actions = ans_clean.getActionMap()

        num_sims = 10
        print('Running MC Sims')
        mcts_hist_rewards = np.zeros((num_sims))
        vi_hist_rewards = np.zeros((num_sims))
        action_list = []
        actual_action_list = []
        perf_list = []
        MC_results_list = []
        VI_rewards = []
        mcts_rewards = []
        perf_R = np.zeros((len(goalList)))
        actual_R = np.zeros((len(goalList)))
        results_list = np.zeros((num_sims))
        reward_list = np.zeros((len(goalList)))
        actual_results = np.zeros((len(goalList)))

        #From VI we need, rewards from MC
        #From MCTS we need, actions, results, rewards


        #print reward, action_lis, result
        for sim in range(num_sims):
            act_row = []
            print('runnning sim:', sim)
            mcts_hist_rewards[sim], MC_actions, results_list[sim] = ans_clean.solveMCTS(startLoc,costmap,goalLoc,1)
            print results_list
            act_row.append(MC_actions)
            action_list.append(act_row)

            vi_hist_rewards[sim],x,y = ans_clean.MCSample(startLoc,actions)
        MC_results_list.append(results_list)             
        VI_rewards.append(vi_hist_rewards)
        mcts_rewards.append(mcts_hist_rewards)


        actual_act_row = []
        actual_R[i], actual_actions, actual_results[i] = ans_clean.solveMCTS(startLoc,costmap,goalLoc,0)
        actual_act_row.append(actual_actions)
        actual_action_list.append(actual_actions)

        perf_row = []
        perf_actions, pr = ans_clean.perfSample(startLoc, actions)
        perf_row.append(perf_actions)
        perf_list.append(perf_row)
        perf_R[i] = pr

            

        policyItem = {'scaledGoal' : goalLoc,
                        'goal' : rawGoalLoc,
                        #'actionMap' : ans.getActionMap(),
                        'actionMapClean' : ans_clean.getActionMap(),
                        'MCSims' : mcts_rewards,
                        'VIMC' : VI_rewards,
                        'MCActions' : action_list,
                        'MCResults' : MC_results_list,
                        'actualActions' : actual_action_list,
                        'actualR' : actual_R,
                        'actualResults' : actual_results,
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
