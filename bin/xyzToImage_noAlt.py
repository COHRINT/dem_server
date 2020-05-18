#!/usr/bin/python2
#Convert a .xyz output from Meshlab into a raster image for use as a DEM to be loaded into a ROS node


import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import pickle, pprint
import copy


#Basic idea:
'''
Take in the desired width/height and the raster's floating point width/height
Quick and dirty: Check if a pixel has been touched. If not, touch it the first time we can. 
Keep track of a running average of what hte height should be for all pixels that contribute to the map
Needs a buffer of some number of rows (floating point - rows 0.0-> 0.99999, cols 0.0 -> 0.9999 contribute to row 0, pixel 1
'''

#Make a raw bitmap using every row for starters

def saveImage(img, fileName):
    maxVal = np.amax(img)
    print 'Rescaling to a max of ', maxVal
    scaledImage = img / maxVal * 255.0
    cv2.imwrite(fileName, scaledImage.astype(np.uint8))


def makeGrayImage(img,fp):
    i = -1
    haz = 0
    for line in fp:
        i+=1
        j = -1
        if i == 20:
            break
        for element in line:
            j+=1
            
            if j == 20:
                break
            
            if element == '0':
                img[i][j] = 0
                haz+=1
            else:
               img[i][j] = 255
               
    #img[0][0] = 0
    #img[19][19] = 255
    print('%3d hazards of 400 possible' % haz)
    return img.astype(np.uint8)

def makeGridStats(img, scale):
    #Given a source image (and scale), grid it up and compute stats for each grid. If var > thresh, its an obstacle...
    
    gridWidth = int(1/scale) #int(img.shape[1]*scale)
    gridHeight = int(1/scale) #int(img.shape[0]*scale)

    output = np.zeros((int(img.shape[0]*scale), int(img.shape[1]*scale)), dtype=np.float32)
    
    
    for row in range(0, int(img.shape[0]/ gridHeight)):
       
        for col in range(0, int(img.shape[1]/gridWidth)):
            #iterating over all grids in the subsampled image
            #print 'Slice:',  gridHeight*row, ' ',  gridHeight*(row+1), ' to ', gridWidth*col , ' ',  gridWidth*(col+1)
            
            gridPix = img[gridHeight*row: gridHeight*(row+1), gridWidth*col: gridWidth*(col+1)]
            #print 'GridPix:', gridPix
            #print 'Var:', np.var(gridPix)
            
            output[row][col] = np.var(gridPix)

            
            '''
            for rawRow in range(gridHeight*row, gridHeight*(row+1)):
                for rawCol in range(gridWidth*col, gridWidth*(col+1)):
                    #Iterating over raw pixels in the grid
            '''
    #print 'Output:', output

    return output


def main():
    if len(sys.argv) < 3:
        print 'usage: ', sys.argv[0], ' <width> <points.xyz> <scale>'
        sys.exit(0)

    width = sys.argv[1]
    fileName = sys.argv[2]
    scale = float(sys.argv[3])
    choice = sys.argv[4]

    
    #Read in the file
    splits = fileName.split('.')
    if splits[1] == 'xyz':
        src = np.loadtxt(fileName, usecols=(1,))
        np.save('%s.npy' % (splits[0]), src)
    elif splits[1] == 'npy':
        src = np.load(fileName)
        
    srcImage = np.reshape(src, (-1, int(width)))
    print 'Made shape:', srcImage.shape


    
    fp = open(choice)

    '''
    Broad image processing steps:
    1. Scale to a grayscale image, with 0 being the lowest el, 255 being the highest
    2. Threshold off bottom 10%
    3. Threshold off top 10%
    4. Binarize
    5. Downscale
    6. Save pickle
    '''


    statImage = makeGridStats(srcImage, scale)
    grayscale = makeGrayImage(statImage,fp)

    #showImage(grayscale)
    fp.close()

    #downsample the obstacle map and save

    print 'Using scale factor %1.3f' % scale
    
    #    obsMap = cv2.resize(thresh_high, (0,0), fx=scale, fy=scale, interpolation = cv2.INTER_NEAREST)


    thresh, obsMap = cv2.threshold(grayscale, 10, 255, cv2.THRESH_BINARY)
    #compImage(grayscale,obsMap)
    np.save('%s_%1.3f.npy' % ('hazmap', scale), obsMap)

    #Corrupt the hazard map by making areas that are obstacles ( draw in 255s) and are clear (draw in 0):
    #Draw 5 circles with radii drawn from U[1,3] and centers drawn from U[1,N][1,N]:
    #Bernoulli flip the clear/haz flag as well evenly
    numCircles = 5
    corruptMap = np.copy(obsMap)


        #print 'Center:', center, ' Radius:', radius, ' Color:', color
   # cv2.circle(corruptMap, center, radius, color, thickness=-1) #filled circle
    print 'Saving hazard package pickle'
    
    #Make a pickle including the raw image and the hazmap associated with it
    output = {'src': srcImage,
              'hazmap': corruptMap,
              'hazmap_clean': obsMap,
              'scale': scale}
    pfile= open('%s.pkl' % 'hazpackage', 'wb')
    #Prepare some plots to verify that the images weren't corrupted (transposed, etc)
    plt.imshow(srcImage, cmap='binary', alpha=0.75)
    #plt.imshow(cv2.resize(corruptMap, srcImage.shape), cmap='binary',alpha=0.5)
    plt.imshow(cv2.resize(obsMap, srcImage.shape, interpolation=cv2.INTER_NEAREST), cmap='binary',alpha=0.5)

    #plt.imshow(corruptMap, cmap='binary',alpha=0.5)
    #plt.imshow(obsMap, cmap='binary',alpha=0.5)
    plt.ylim(max(plt.ylim()), min(plt.ylim()))

    plt.show()
    pickle.dump(output, pfile)

if __name__ == "__main__": main()