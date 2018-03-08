#!/usr/bin/python2
#Convert a .xyz output from Meshlab into a raster image for use as a DEM to be loaded into a ROS node


import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import pickle, pprint

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
    if len(sys.argv) < 3:
        print 'usage: ', sys.argv[0], ' <width> <points.xyz> <scale>'
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

    #downsample the obstacle map and save

    scale = float(sys.argv[3])
    print 'Using scale factor %1.3f' % scale
    
    obsMap = cv2.resize(thresh_dil, (0,0), fx=scale, fy=scale, interpolation = cv2.INTER_NEAREST)
    saveImage(obsMap, 'obsMap.png')
    np.save('%s_%1.3f.npy' % ('hazmap', scale), obsMap)

    #Corrupt the hazard map by making areas that are obstacles ( draw in 255s) and are clear (draw in 0):
    #Draw 5 circles with radii drawn from U[1,3] and centers drawn from U[1,N][1,N]:
    #Bernoulli flip the clear/haz flag as well evenly
    
    numCircles = 2
    corruptMap = np.copy(obsMap)

    print 'Drawing ', numCircles, ' corruptions in the map'
    for i in range(0,numCircles):
        center = (int(np.random.uniform(low=0.0, high=obsMap.shape[0])),
                  int(np.random.uniform(low=0.0, high=obsMap.shape[1])))
        radius = int(np.random.uniform(low=1.0, high=3.0))
        color = 0 if np.random.uniform() > 0.5 else 255

        #print 'Center:', center, ' Radius:', radius, ' Color:', color
        cv2.circle(corruptMap, center, radius, color, thickness=-1) #filled circle

    print 'Saving hazard package pickle'
    
    #Make a pickle including the raw image and the hazmap associated with it
    output = {'src': srcImage,
              'hazmap': corruptMap,
              'hazmap_clean': obsMap,
              'scale': scale}
    pfile= open('%s.pkl' % 'hazpackage', 'wb')
    pickle.dump(output, pfile)
    
    #Prepare some plots to verify that the images weren't corrupted (transposed, etc)
    #plt.imshow(srcImage, cmap='binary', alpha=0.75)
    #plt.imshow(cv2.resize(corruptMap, srcImage.shape), cmap='binary',alpha=0.5)
    #plt.imshow(cv2.resize(obsMap, srcImage.shape), cmap='binary',alpha=0.5)

    plt.imshow(corruptMap, cmap='binary',alpha=0.5)
    plt.imshow(obsMap, cmap='binary',alpha=0.5)
    plt.ylim(max(plt.ylim()), min(plt.ylim()))

    plt.show()
if __name__ == "__main__": main()
