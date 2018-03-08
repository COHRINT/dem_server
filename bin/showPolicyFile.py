#!/usr/bin/python2
import pickle, pprint
import sys
scale = 0.01
pfile = open(sys.argv[1], 'rb')
print 'Pickle contents:', pickle.load(pfile)

