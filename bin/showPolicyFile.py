#!/usr/bin/python2
import pickle, pprint
import sys
scale = 0.01
pfile = open(sys.argv[1], 'rb')
contents = pickle.load(pfile)
print 'Pickle contents:', contents
print 'DEM src shape:', contents['src'].shape
print 'Reduced hazmap shape:', contents['hazmap'].shape

