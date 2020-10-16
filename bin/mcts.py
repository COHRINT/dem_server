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



class SolverMCTS():


    def __init__(self, modelName=None, *args, **kwds):

        # print 'Args:', args
        # print 'KWArgs:', kwds
        #Time Discount
        self.gamma = .9; 

        #Number of Actions
        self.numActions = 3;

        #Max solver time per action
        self.maxTime = 1; #max time I spend searching

        #Exploration Constant
        self.c = 1;  

        if modelName == None:
            print('MDPSolver: Provide a Python class implementing type ModelSpec')
            return
        print('Using MCTS model:', modelName)
        modelModule = __import__(modelName, globals(),
                                 locals(), [modelName], 0)

        classes = [c for c in modelModule.__dict__.values()
                   if isinstance(c, type)]
        base_subclasses = [c for c in classes if issubclass(c, ModelSpec)]
        # print 'Model class:', base_subclasses[-1]

        self.model = base_subclasses[-1](*args, **kwds)




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
        sprime = self.generate_s(s,act)
        r = self.generate_r(s, act)


        # # if this is the first time you've seen this node
        if(len(h[act].children) == 0):
            for a in range(0,self.numActions):
                h[act].addChildID(a); 
                h[act][a].N = 1;
            #return self.rollout(s,depth); #Choice here
            return self.estimate_value(s);

            #return r which r is it 
        q = r + self.gamma * \
            self.simulate(sprime, h[act], depth-1)

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
            self.simulate(s, h, depth)
        #print([a.Q for a in h]); 
        return np.argmax([a.Q for a in h]) #approximation of value function


    def generate_s(self,s,a): #random choice with state and action
        sprime = s; 
        if(a == 0):
            #go left
            sprime = s-1; 
        elif(a==1):
            #go right
            sprime = s+1;
        elif(a == 2):
            #stay
            sprime = s; 

        #Make sure you stay in bounds
        sprime = max(-10,min(10,sprime)); 

        return sprime; 

    def generate_r(self,s,a): #query new reward
        if(s==4 and a==2):
            return 10; 
        else:
            return -1; 


    def isTerminal(self,s,a): #check if we go to goal or obstacle
        if(s==4 and a == 2):
            return True; 
        else:
            return False; 

    def rollout(self,s,depth): #rollouts beyond known tree
        if(depth <= 0):
            return -1

        # random action
        act = np.random.randint(0, 3) #maybe hueristic for d(goal), action that will take me closest to goal
        sprime = self.generate_s(s, act)
        r = self.generate_r(s, act)

        return r + self.gamma*self.rollout(sprime, depth-1)

    def estimate_value(self,s): #Hack: this node you saw for the first time, is as valuble as 10-dist2goal
        return 10-np.abs(4-s); 

    def testMCTS_Sim(self):
        solver = SolverMCTS(); 

        #Starting state
        state = -4; 

        #Set max depth
        maxDepth = 15; #breadth vs depth

        count = 0; 
        while(count < 100):
            h = Node(); 
            act = solver.search(state,h,maxDepth); #fake
            r = solver.generate_r(state,act); #generate reward for that fake action
            print("State: {}, Action: {}, Reward: {}".format(state,act,r)); 
            tmp = ''; 
            for i in range(-10,11):
                if(i==state):
                    tmp += "R"; 
                elif(i==4):
                    tmp += 'G'; 
                else:
                    tmp += '-'; 
            print(tmp); 
            if(state == 4 and act == 2):
                print("Goal Reached"); 
                break; 

            state = solver.generate_s(state,act); #actually move transition[h]

            print(""); 
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