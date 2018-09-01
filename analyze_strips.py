import strip_analysis_classes as sistrip
import sys
import argparse
import re
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

parser = argparse.ArgumentParser(description='Reads LabView strip measurement output file. Uses measurements to make plots and output formatted data to a text file. This file uses the custom classes written in "strip_analysis_classes.py"')
parser.add_argument('file', help='Required input, tells script which text file to read')
parser.add_argument('-r', '--root', help='''Create a ROOT file with the parsed measurements.
                    You must have the pyroot library installed to use this otion.
                    \nThis is False by default''',
                    action='store_true', default='store_false')
parser.add_argument('-k', '--keep_all', help='''If you have multiple measurements
                    with the same strip measurement, the script will replace the previous
                    measurement with the new one. Using this option will instead keep all
                    of the measurements.
                    \nThis is False by default.''', action='store_false', default='store_true')

#if the LabView output file changes, this is the method which must be edited
def readFile(filename, keep):
    f = open(filename, "r").readlines()
    cc_offsent = 0.0
    ic_offset = 0.0
    sensor = sistrip.sensor()
    strip_meas = sistrip.strip()
    first_strip = True #used to determine if first strip or not
    iv = [] #used for calculating res of IV curves, bad notation because the form is [i,v]
    for line in f:
        iv = []
        #look for open cap measurements
        if 'MHz' in line:
            if 'Not Measured' not in line:
                cc_offset=float(line.split()[5])
                print "Coupling Cap offset is", cc_offset
                ic_offset=float(line.split()[6])
                print "Interstrip Cap offset is", ic_offset
            else:
                if line.split()[5] == 'Not':
                    cc_offset = 0.0
                    if line.split()[7] != 'Not':
                        ic_offset = float(line.split()[7])
                else:
                    cc_offset = float(line.split()[5])
        #get strip number
        elif 'Strip' in line:
            #see if this is the first strip. If not, append the previous set of measurements to the "sensor" variable and clear the variable.
            if first_strip == False:
                sensor.add_strip(strip, keep)
                strip.clear()
            else: first_strip = True
            strip_meas.add_meas('strip', float(line.split()[1]))
        #get chuck temperature
        elif 'ChuckT' in line:
            #the weird stuff in split is basically just telling it to split at the boundary of chars and numbers
            strip_meas.add_meas('chuckT', float(re.split('(\d+\.\d+)',line)[1]))
        #get air temperature
        elif 'airT' in line:
            strip_meas.add_meas('airT', float(re.split('(\d+\.\d+)',line)[1]))
        #get humidity
        elif 'Humidity' in line:
            strip_meas.add_meas('humid', float(re.split('(\d+\.\d+)',line)[1]))
        #get pinhole
        elif 'Pinhole' in line:
            strip_meas.add_meas('pinhole', float(line.split()[1]))
        #get coupling cap
        elif 'Coupling Cap' in line:
            strip_meas.add_meas('coupC', float(line.split()[2]) - cc_offset)
        #get interstrip capacitence
        elif 'Interstrip C' in line:
            strip_meas.add_meas('interC', float(line.split()[2]) - ic_offset)
        #get the global current
        elif 'Global IV' in line:
            strip_meas.add_meas('bias', float(next(line)))
        #get the leakage current
        elif 'Ileak' in line:
            strip_meas.add_meas('ileak', float(next(line).split()[1]))
        #get poly resistance
        # for resistance measurements, you need to fit a straight line to an IV curve
        # the first data points used is the leakage current at V = 0
        # script then looks at the following lines. If it sees that the line is not empty (\n)
        # it will then add the voltage and current measurements to a list
        # it then calls the function calc_res which just fits a straight line to the data
        # points and returns the slope
        elif 'RBias' in line:
            if strip_meas.get_meas('ileak') != 0:
                iv.append([0.0, strip_meas.get_meas('ileak')])
            i = 1
            while True:
                if line.next(i) != '\n':
                    iv.append([float(line.next(i).split()[0]),float(line.next(i).split()[1])])
                    i+=1
                else: break
            strip_meas.add_meas('rbias', calc_res(iv))
        #get leakage current from neighboring strip
        # note there is a typo from labview, if the typo is fixed
        # this elif statement needs to be fixed too
        elif 'DC Neihbor ILeak' in line:
            strip_meas.add_meas('ileaknbr', float(line.next().split()[1]))
        elif 'RBNbr' in line:
            if strip_meas.get_meas('ileaknbr') != 0.0:
                iv.append(0, strip_meas.get_meas('ileaknbr'))
            i = 1
            while True:
                if line.next(i) != '\n':
                    iv.append([float(line.next(i).split()[0]),float(line.next(i).split()[1])])
                    i+=1
                else: break
            strip_meas.add_meas('rbiasnbr', calc_res(iv))
        elif 'Interstrip R' in line:
            i = 1
            while True:
                if line.next(i) != '\n':
                    iv.append([float(line.next(i).split(0)),float(line.next(i).split()[1])])
                else: break
            strip_meas.add_meas('interR', calc_res(iv))
    return sensor

#Makes an IV curve to calculate the resistance
#For rbias, uses the leakage current as the point (ileak, 0V)
def calc_res(iv):
    volt = iv[0,:]
    curr = iv[1,:]
    fit = np.polyfit(curr, volt, 1)
    return fit[0]

#makes the plots of the data on linear and log y scales
# the function first checks which measurements were taken
# it then takes an array consiting of 
def plotter(sensor):
    return 0

def makeRoot():
    return 0


def main():
    args=parser.parse_args()
    sensor = readFile(args.file, args.keep_all)
    print sensor
    if args.root:
        makeRoot()

if __name__ == '__main__':
    main()
