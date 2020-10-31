#!/usr/bin/python2
import time
import numpy as np
from treeNode import Node
from ModelSpec import *
from Location import *

############################################
#file: mcts.py
#Date: May 2020
#Author: Luke Burks
#
# Simple hallway problem implementation
# 
# -----R-------G------
#
# Robot can move left and right on [-10,10]
# Objective is to choose "stay" action 
# at goal location [4]
############################################




def simulate(self, s, h, depth): #fake 


    # check if node is in tree
    # if not, add nodes for each action
    if(depth <= 0):
        return 0

    #Add all possible actions to nodes children
    if(len(h.children) == 0): 
        for a in range(0,self.numActions):
            h.addChildID(a)
            h[a].N = 1; 


    # find UCT algorithms suggested action
    act = np.argmax([ha.Q + self.c*np.sqrt(np.log(h.N)/ha.N) for ha in h])

    # generate s,r
    sprime = self.generate_s(self,s,act)
    r = generate_r(self,s, act)


    # # if this is the first time you've seen this node
    if(len(h[act].children) == 0):
        for a in range(0,self.numActions):
            h[act].addChildID(a); 
            h[act][a].N = 1;
        return rollout(self,s,depth); #Choice here
        #return self.estimate_value(s);

        #return r which r is it 
    q = r + self.gamma * \
        simulate(self,sprime, h[act], depth-1)

    # update node values
    h.N += 1
    h[act].N += 1
    h[act].Q += (q-h[act].Q)/h[act].N



    return q


def search(self, s, h, depth):
    count = 0

    startTime = time.clock()

    while(time.clock()-startTime < self.maxTime): 
        count += 1
        simulate(self,s, h, depth)
    #print([a.Q for a in h]); 
    return np.argmax([a.Q for a in h]) #approximation of value function


def generate_s(self,s,a): #random choice with state and action
    current = np.random.choice(range(self.model.N),p=self.model.px[a][s][:])

    return current; 

def generate_r(self,s,a): #query new reward
    return self.model.R_values[s]


def isTerminal(self,s,a): #check if we go to goal or obstacle
    if self.model.R_values[s] not in [self.model.obstacleReward,self.model.goalReward]:
        return True;
    else:
        return False;

def rollout(self,s,depth): #rollouts beyond known tree
    if(depth <= 0):
        return -1

    # random action
    [x,y] = self.convertToGridCoords(s,self.model.width,self.model.height)
    act = self.actions[y][x].value
    sprime = self.generate_s(s, act)
    r = self.generate_r(s, act)

    return r + self.gamma*self.rollout(sprime, depth-1)

def estimate_value(self,s): #Hack: this node you saw for the first time, is as valuble as 10-dist2goal
    return 400-np.abs(2-s); 



def convertToGridCoords(self,i, width, height):
    y = i//width
    x = i % width
    return x, y
def testMCTS_Once():
    solver = SolverMCTS(); 

    #Starting state
    state = 1; 

    #Initialize Tree
    h = Node(); 

    #Set max depth
    maxDepth = 15; 

    act = solver.search(state,h,maxDepth); 


    print(act); 



if __name__ == '__main__':
    #testMCTS_Once(); 
    class1 = SolverMCTS()
    class1.testMCTS_Sim(class1);