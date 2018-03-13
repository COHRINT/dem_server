#!/usr/bin/python2

'''
ROS node to suck in a policy package pickle and do the following things:
1. Publish the raw DEM source image as a map
2. Publish the hazard map as known to the server (the corrupted one)
3. Publish current goal (if any)

4. Subscribe to Unity/Pose
OnNewMessage: 
Query MDP for current steer based on pose and scale
Publish steer angle

Services: 
GetGoalList (returns ID and coords)
SetCurrentGoalByID

'''

import rospy
from traadre_msgs.msg import *
from traadre_msgs.srv import *
from geometry_msgs.msg import *
from sensor_msgs.msg import *
from Location import *

import sys, pickle
import numpy as np
import cv_bridge
import cv2

class PolicyServer(object):
    def __init__(self):
        print 'Starting policy server'
        self.nodeName = 'policy_server'
        rospy.init_node(self.nodeName)
        
        self.polPack = self.loadPolicyPackage()

        #print self.polPack
        
        #Initialize services
        self.currentSteer = Steering()
        
        self.setGoalSrv = rospy.Service('~SetCurrentGoal', SetCurrentGoal, self.setCurrentGoalByID)
        self.getGoalSrv = rospy.Service('~GetGoalList', GetGoalList, self.getGoalList)
        
        #Publish maps and things
        self.demPub = rospy.Publisher('dem', Image, queue_size=10, latch=True)
        self.hazPub = rospy.Publisher('hazmap', Image, queue_size=10, latch=True)
        self.goalPub = rospy.Publisher('current_goal', Pose2D, queue_size=10, latch=True)
        self.steerPub = rospy.Publisher('current_steer', Steering, queue_size=10, latch=True)
        
        self.publishDEM()
        self.publishHazmap()

        #Subscribe to a PoseStamped topic for the current robot position
        self.poseSub = rospy.Subscriber('pose', PoseStamped, self.onNewPose)
        
        print 'Policy server ready!'

     
    def publishDEM(self):
        self.demPub.publish(cv_bridge.CvBridge().cv2_to_imgmsg(self.polPack['src'], encoding='64FC1'))
        print 'DEM published'
        
    def publishHazmap(self):
        hazRaw = self.polPack['hazmap']
        #Invert to match ROS convention of white=traversable

        self.hazPub.publish(cv_bridge.CvBridge().cv2_to_imgmsg(cv2.bitwise_not(hazRaw), encoding='mono8'))
        
    def loadPolicyPackage(self):
        #Load a policy package from the pickle
        polFile = rospy.get_param('~policy', None)
        if polFile is None:
            print 'Parameter policy not defined'
            return None

        print 'Loading policy package from:', polFile
        pFile = open(polFile, 'rb')
        return pickle.load(pFile)
    
    def onNewPose(self, msg):
        #Query the policy for the current goal with the current position and publish the appropriate
        #action extracted from the policy
        
        #no goal has been set yet
        if self.currentSteer.id == '':
            return
        
        thePolicy = self.polPack['policies'][self.currentSteer.id]

        actionMap = thePolicy['actionMap']
        #print 'Policy:', actionMap

        #Get the current (scaled) position:
        scaledX = int(msg.pose.position.x * self.polPack['scale'])
        scaledY = int(msg.pose.position.y * self.polPack['scale'])

        #Get the location:
        print 'Checking X:', scaledX, ' Y:', scaledY
        
        steerLoc = actionMap[scaledY][scaledX]

        #Convert to degrees:
        if(steerLoc == Location.Forward):
	    steerAngle = 90.0
	elif(steerLoc == Location.FwdRight):
            steerAngle = 45.0
        elif(steerLoc == Location.Right):
            steerAngle = 0.0
        elif(steerLoc == Location.BackRight):
            steerAngle = 315.0
        elif(steerLoc == Location.Back):
            steerAngle = 270.0
        elif(steerLoc == Location.BackLeft):
            steerAngle = 225.0
        elif(steerLoc == Location.Left):
            steerAngle = 180.0
        elif(steerLoc == Location.FwdLeft):
            steerAngle = 135.0
        else:
            #We've arrived at the goal - don't publish a new steer
            return

        self.currentSteer.steer = int(steerAngle)
        self.currentSteer.header.stamp = rospy.Time.now()
        
        self.steerPub.publish(self.currentSteer)
        
    def getGoalList(self, req):
        res = GetGoalListResponse()

        #Publish things out of the polPackage dictionary
        for goalID, policy in self.polPack['policies'].iteritems():
            #print 'Policy:', policy
            
            res.ids.append(goalID)
            polGoal =  policy['goal']
            theGoal = Pose2D(polGoal[0], polGoal[1], 0.0)
            res.goals.append(theGoal)
        return res

    def setCurrentGoalByID(self, req):
        res = SetCurrentGoalResponse()

        #Look for a goal with the given id:
        for policyID in self.polPack['policies']:
            if policyID == req.id:
                polGoal = self.polPack['policies'][policyID]['goal']
                res.goal = Pose2D(polGoal[0], polGoal[1], 0.0)
                break;

        print 'Setting desired goal: ', req.id, ' X:', res.goal.x, ' Y:', res.goal.y
        self.currentSteer.goal = res.goal
        self.currentSteer.id = req.id


        self.goalPub.publish(res.goal)
        
        return res
    
    def run(self):
        rospy.spin()
        
if __name__ == "__main__":
    server = PolicyServer()
    server.run()
    
