#!/usr/bin/python2
import pickle, pprint
import sys
import numpy as np
from Location import * 
import matplotlib.pyplot as plt

scale = 0.01

def main():
    pfile = open(sys.argv[1], 'rb')
    contents = pickle.load(pfile)
    #print 'Pickle contents:', contents
    print 'DEM src shape:', contents['src'].shape
    print 'Reduced hazmap shape:', contents['hazmap'].shape

    scale = contents['scale']
    print 'Scale:', scale

    for goalID in contents['policies']:
        print goalID, ': goal (row,col):', contents['policies'][goalID]['goal'],
        #print 'scaledGoal:', contents['policies'][goalID]['scaledGoal']
        #Plot this policy with some viz
        checkBoth2D(contents['hazmap'], contents['scale'], contents['policies'][goalID])

def convertToGridCoords(i, width):
    y = i//width; 
    x = i%width; 
    return x,y;

def checkBoth2D(hazMap, scale, policy):
    #print 'Policy:', policy
    actionMap = policy['actionMap']

    arrowGridAngle = np.zeros(np.array(actionMap).shape);

    print 'Action height:', len(actionMap)
    print 'Action width:', len(actionMap[0])
    
    for y in range(0,len(actionMap)):
            for x in range(0,len(actionMap[0])):
                    if(actionMap[y][x] == Location.Forward):
                            arrowGridAngle[y][x] = 90.0
                    elif(actionMap[y][x] == Location.FwdRight):
                            arrowGridAngle[y][x] = 45.0
                    elif(actionMap[y][x] == Location.Right):
                            arrowGridAngle[y][x] = 0.0
                    elif(actionMap[y][x] == Location.BackRight):
                            arrowGridAngle[y][x] = 315.0
                    elif(actionMap[y][x] == Location.Back):
                            arrowGridAngle[y][x] = 270.0
                    elif(actionMap[y][x] == Location.BackLeft):
                            arrowGridAngle[y][x] = 225.0
                    elif(actionMap[y][x] == Location.Left):
                            arrowGridAngle[y][x] = 180.0
                    elif(actionMap[y][x] == Location.FwdLeft):
                            arrowGridAngle[y][x] = 135.0

    X,Y = np.mgrid[0:arrowGridAngle.shape[0]:1, 0:arrowGridAngle.shape[1]:1]

    #Quiver plot angles go counter-clock from horiz axis
    
    plt.quiver(X,Y,angles=arrowGridAngle,color='k');
    #Since goals are in (row, col), swap indices for the scatter call
    plt.scatter(int(policy['goal'][1]*scale), int(policy['goal'][0]*scale),c='c',s=250,marker='*')

    plt.imshow(hazMap, alpha=0.5,cmap='binary')
    plt.title('MDP Policy, goal: (%d, %d)' % (policy['goal'][0]*scale, policy['goal'][1]*scale));
    plt.ylim(max(plt.ylim()), min(plt.ylim()))

    plt.show();

if __name__ == "__main__":
    main()
