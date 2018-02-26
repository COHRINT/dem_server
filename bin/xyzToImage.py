#!/usr/bin/python2
#Convert a .xyz output from Meshlab into a raster image for use as a DEM to be loaded into a ROS node


import cv2
import numpy as np
import sys

#Basic idea:
'''
Take in the desired width/height and the raster's floating point width/height
Quick and dirty: Check if a pixel has been touched. If not, touch it the first time we can. 
Keep track of a running average of what hte height should be for all pixels that contribute to the map
Needs a buffer of some number of rows (floating point - rows 0.0-> 0.99999, cols 0.0 -> 0.9999 contribute to row 0, pixel 1

'''

#Make a raw bitmap using every row for starters

def showImage(img):
    maxVal = np.amax(img)
    print 'Rescaling to a max of ', maxVal
    scaledImage = img / maxVal * 255.0
    cv2.imshow('Source image', scaledImage)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 27: break 
    cv2.destroyAllWindows()

def saveImage(img, fileName):
    maxVal = np.amax(img)
    print 'Rescaling to a max of ', maxVal
    scaledImage = img / maxVal * 255.0
    cv2.imwrite(fileName, scaledImage.astype(np.uint8))
    
def main():
    if len(sys.argv) < 2:
        print 'usage: ', sys.argv[0], ' <width> <points.xyz>'
        sys.exit(0)

    width = sys.argv[1]
    fileName = sys.argv[2]
    #Read in the file
    splits = fileName.split('.')
    if splits[1] == 'xyz':
        src = np.loadtxt(fileName, usecols=(1))
        np.save('%s.npy' % (splits[0]), src)
    elif splits[1] == 'npy':
        src = np.load(fileName)
        
    srcImage = np.reshape(src, (-1, int(width)))
    print 'Made shape:', srcImage.shape

    saveImage(srcImage, 'src_scaled.png')
    
    #Compute a gradient image
    laplacian = cv2.Laplacian(srcImage,cv2.CV_64F)
    laplacian_abs = np.absolute(laplacian)
    
    saveImage(laplacian_abs, 'src_laplace.png')

    #Threshold the gradient image to a set value (since max is 0.8, set to something less than that)
    #This isn't quite what I want - in this code, 0 means passable, white means hazard
    empty, threshImg_f = cv2.threshold(laplacian_abs, 0.25, 255, cv2.THRESH_BINARY)

    threshImg = threshImg_f.astype(np.uint8)
    saveImage(threshImg_f, 'thresh.png')
    
    #Dilate around a kernel to grow the hazard zones
    kernel = np.ones((10,10),np.uint8) 
    thresh_dil = cv2.dilate(threshImg, kernel, iterations = 3)

    saveImage(thresh_dil, 'thresh_dilated.png')
    #This is a float32 image, where the float value is the elevation

    #downsample the obstacle map:

    obsMap = cv2.resize(thresh_dil, (0,0), fx=0.05, fy=0.05, interpolation = cv2.INTER_NEAREST)
    saveImage(obsMap, 'obsMap.png')

if __name__ == "__main__": main()
