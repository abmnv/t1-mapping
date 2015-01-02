#!/usr/bin/env python

import dicom
import argparse
import sys
import numpy
import math

def main():

    parser=argparse.ArgumentParser()

    parser.add_argument("volume1")
    parser.add_argument("alpha1", type=float)
    parser.add_argument("tr1", type=float)

    parser.add_argument("volume2")
    parser.add_argument("alpha2", type=float)
    parser.add_argument("tr2", type=float)

    args = parser.parse_args()

    v1 = dicom.read_file(args.volume1)
    v2 = dicom.read_file(args.volume2)

    # make sure that volumes have the same shape
    if v1.pixel_array.shape != v2.pixel_array.shape:
        print "FATAL ERROR: the size of first volume is not equil the size of second volume"
        sys.exit()
    
    if args.tr1 != args.tr2:
        print "FATAL ERROR: the repetition time should be the same for both images"
        sys.exit()

    #v3 = copy.deepcopy(v1)# the resulting T1 will be saved here
    
    #convert flip angles from degrees to radians
    alpha1 = math.radians(args.alpha1)
    alpha2 = math.radians(args.alpha2)

    #create 2D numpy array to store T1 results
    t1_array = numpy.zeros(v1.pixel_array.shape)
    if t1_array.shape != v1.pixel_array.shape:
        print "problem with creating t1 array"
        sys.exit()

    for i,val in enumerate(v1.pixel_array.flat):

        # apply formula [1] from
        # y = S/sin(alpha)
        # x = S/tan(alpha)
        # Calculate E1 from slop of the line ie, dy/dx
        # Calculate T1 = -TR/ln(E1)
        x1 = v1.pixel_array.flat[i] / math.tan(alpha1)
        y1 = v1.pixel_array.flat[i] / math.sin(alpha1)

        x2 = v2.pixel_array.flat[i] / math.tan(alpha2)
        y2 = v2.pixel_array.flat[i] / math.sin(alpha2)

        e1 = (y2 - y1) / (x2 - x1)# this is slope which is equil to E1

        if e1 <= 0:# when e1 is less than zero it causes underfined number error for log, avoid it by setting t1 to zero
            e1 = 1.0
            t1 = 0
            print "WARNING: e1 is less than zero for pixel ", i, " vol1 value: ", v1.pixel_array.flat[i], " vol2 value: ", v2.pixel_array.flat[i]
        else:
            t1 = -args.tr1/math.log(e1)# this is T1

        #print x1, y1, x2, y2, e1, t1

        t1_array.flat[i] = t1

    #print t1_array[:,::10]
    #print t1_array[:,0]

    numpy.savetxt("t1-sim.dat", t1_array[10::10,::10], fmt='%.2f')

if __name__ == "__main__":
    main()
