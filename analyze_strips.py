#!/usr/bin/python2.7

import strip_analysis_classes as sistrip
import sys
import argparse
import re
import numpy as np

if sys.version_info[0] == 3:
    print '''This script runs using python 2.7. If you have a different version as the default\n
run the program using ./ rather than python to run using correct version of python'''
    sys.exit()

parser = argparse.ArgumentParser(description='''Reads LabView strip measurement output file. Uses measurements to make plots and output formatted data to a text file. This file uses the custom classes written in "strip_analysis_classes.py". I have tried to comment this piece of code a whole lot for anyone who may need to change it in the future :)''')
parser.add_argument('file', help='Required input, tells script which text file to read')
parser.add_argument('-np', '--noplot', action='store_true', help='''Choose to run the script but not produce any plots. Use this flag when running on brux to avoid tkinter errors associated with pyplot''')
parser.add_argument('-r', '--root', help='''Create a ROOT file with the parsed measurements.
                    You must have the pyroot library installed to use this option.
                    \nThis is False by default''', action='store_true')
parser.add_argument('-k', '--keep_all', help='''If you have multiple measurements
                    with the same strip measurement, the script will replace the previous
                    measurement with the new one. Using this option will instead keep all
                    of the measurements.
                    \nThis is False by default.''', action='store_false')
parser.add_argument('-rev', '--reverse', action='store_true',
                    help='''After parsing the labview file, it will reverse the order of
                    the strip number. So, if you started at strip 1024 instead of strip 1,
                    then strip number N will change to strip 1024 - N +1.''')
parser.add_argument('-c', '--check_diff', action='store_true',
                    help='''For ileak and rbias, plots the difference between the measurements
                    when they were taken as the DC pad with the measurement when taken as neighbor''')
parser.add_argument('-mf', '--meas_first', action='store_true',
                    help='''Determines the way that the plot name is ordered.
                    By default, the naming convention for the plot is
                    <filename>_<measurement>.png \n
                    With this option, it will be changed to
                    <measurement>_<filename>.png''')

#if the LabView output file changes, this is the method which must be edited
def readFile(filename, keep):
    file = open(filename, "r").read().splitlines()
    #print file #this is nice for debugging stuff in the for in the while loop
    f = iter(file)
    cc_offsent = 0.0
    ic_offset = 0.0
    sensor = sistrip.sensor()
    strip_meas = sistrip.strip()
    first_strip = True #used to determine if first strip or not
    iv = [] #used for calculating res of IV curves, bad notation because the form is [i,v]
    #loop through the lines in the file and read the data
    # rather than using a standard for loop, this script defines the list of lines "f"
    # as a iterator and uses a while loop to manually loop through the lines
    # the reason the code does it this way is because based on the content of a line of
    # text I may need to access information on the next line(s). Because the number
    # of measurements for a resistance measurements can be a variable number
    # I did not want to use the zip command to hard code in the number of measurements
    # I would take. This is just the fastest and easiest to understand way
    # to do this that I could think of
    line = f.next()
    while True:
        iv = []
        #print line
        #print first_strip
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
            line = f.next()
            continue
        #get strip number
        elif 'Strip' in line:
            #see if this is the first strip. If not, append the previous set of measurements to the "sensor" variable and clear the variable.
            if first_strip == False:
                sensor.add_strip(strip_meas, keep)
                strip_meas.clear()
            else: first_strip = False
            strip_meas.add_meas('strip', int(line.split()[1]))
            line = f.next()
            continue

        ##### For T and H measurements, this splitting does not pick up sci notation. Labview script needs to be edited to output names correctly ####

        #get chuck temperature
        elif 'ChuckT' in line:
            #the weird stuff in split is basically just telling it to split at the boundary of chars and numbers
            strip_meas.add_meas('chuckT', float(re.split('(\d+\.\d+)',line)[1]))
            line = f.next()
            continue
        #get air temperature
        elif 'AirT' in line:
            strip_meas.add_meas('airT', float(re.split('(\d+\.\d+)',line)[1]))
            line = f.next()
            continue
        #get humidity
        elif 'Humidity' in line:
            strip_meas.add_meas('humid', float(re.split('(\d+\.\d+)',line)[1]))
            line = f.next()
            continue
        #get pinhole
        elif 'Pinhole' in line:
            strip_meas.add_meas('pinhole', float(line.split()[1]))
            line = f.next()
            continue
        #get coupling cap
        elif 'Coupling Cap' in line:
            strip_meas.add_meas('coupC', float(line.split()[2]) - cc_offset)
            line = f.next()
            continue
        #get interstrip capacitence
        elif 'Interstrip C' in line:
            strip_meas.add_meas('interC', float(line.split()[2]) - ic_offset)
            line = f.next()
            continue
        #get the global current
        elif 'Global IV' in line:
            line = f.next()
            strip_meas.add_meas('bias', float(line))
            line = f.next()
            continue
        #get the leakage current
        elif 'Ileak' in line:
            line = f.next()
            strip_meas.add_meas('ileak', float(line.split()[1]))
            line = f.next()
            continue
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
            line = f.next()
            while line != '':
                iv.append([float(line.split('\t')[0]),float(line.split('\t')[1])])
                line = f.next()
            strip_meas.add_meas('rbias', calc_res(iv))
            continue
        #get leakage current from neighboring strip
        # note there is a typo from labview, if the typo is fixed
        # this elif statement needs to be fixed too
        elif 'DC Neihbor ILeak' in line:
            line = f.next()
            strip_meas.add_meas('ileaknbr', float(line.split()[1]))
            line = f.next()
            continue
        elif 'RBNbr' in line:
            if strip_meas.get_meas('ileaknbr') != 0.0:
                iv.append([0, strip_meas.get_meas('ileaknbr')])
            line = f.next()
            while line != '':
                iv.append([float(line.split('\t')[0]),float(line.split('\t')[1])])
                line = f.next()
            strip_meas.add_meas('rbiasnbr', calc_res(iv))
            continue
        elif 'Interstrip R' in line:
            line = f.next()
            while line != '':
                iv.append([float(line.split('\t')[0]),float(line.split('\t')[1])])
                line = f.next()
            strip_meas.add_meas('interR', calc_res(iv))
            continue
        try:
            line = f.next()
        except StopIteration:
            break
    return sensor

#Makes an IV curve to calculate the resistance
#For rbias, uses the leakage current as the point (ileak, 0V)
def calc_res(iv):
    volt = [elm[0] for elm in iv]
    curr = [elm[1] for elm in iv]
    fit = np.polyfit(curr, volt, 1)
    return fit[0]

#makes the plots of the data on linear and log y scales
# the function first checks which measurements were taken
# it then makes log and linear plots of the plots that were taken
def plotter(sensor, filename, meas_first):
    try:
        import matplotlib.pyplot as plt
    except:
        print 'Trying to plot but getting error when importing pyplot. Skipping plotting step'
        return
    import matplotlib.gridspec as gridspec
    sensor.check_measurements()
    filename = filename[:-4]
    for meas in sensor.meas_taken():
        if not sensor.meas_taken()[meas]: continue
        if meas == 'strip':
            continue
        print "making", meas, "plot"
        plt.figure()
        #data = sensor.get_meas_list(meas)
        data = sensor.get_meas(meas)
        plt.plot(data, '-r.')
        plt.grid()
        plt.xlabel('Strip Number')
        title = ''
        meas_str = ''
        log = True
        if meas == 'ileak':
            plt.suptitle('Leakage Current')
            plt.ylabel('Current (A)')
            meas_str = 'strip_leakage_current'
        elif meas == 'ileaknbr':
            plt.suptitle('Neighbor Strip Leakage Current')
            plt.ylabel('Current (A)')
            meas_str = 'nbr_leakage_current'
        elif meas == 'rbias':
            plt.suptitle('Polyresistor Resistance')
            plt.ylabel('Resistance ($\Omega$)')
            meas_str = 'strip_polyresistance'
        elif meas == 'rbiasnbr':
            plt.suptitle('Neighbor Polyresistor Resistance')
            plt.ylabel('Resistance ($\Omega$)')
            meas_str = 'nbr_polyresistance'
        elif meas == 'pinhole':
            plt.suptitle('Pinhole Current')
            plt.ylabel('Current (A)')
            meas_str = 'strip_pinhole'
        elif meas == 'bias':
            plt.suptitle('Global Current')
            plt.ylabel('Current (A)')
            meas_str = 'global_current'
        elif meas == 'coupC':
            plt.suptitle('Coupling Capacitance')
            plt.ylabel('Capacitance (F)')
            meas_str = 'strip_coupling_cap'
        elif meas == 'interC':
            plt.suptitle('Interstrip Capacitance')
            plt.ylabel('Capacitance (F)')
            meas_str = 'interstrip_cap'
        elif meas == 'interR':
            plt.suptitle('Interstrip Resistance')
            plt.ylabel('Resistance ($\Omega$)')
            meas_str = 'interstrip_res'
        elif meas == 'airT':
            plt.suptitle('Air Temperature')
            plt.ylabel('Temperature ($^{\circ}$C)')
            meas_str = 'environment_air_temp'
            log = False
        elif meas == 'chuckT':
            plt.suptitle('Chuck Temperature')
            plt.ylabel('Temperature ($^{\circ}$C)')
            meas_str = 'environment_chuck_temp'
            log = False
        elif meas == 'humid':
            plt.suptitle('Relative Humidity')
            plt.ylabel('Humidity %')
            meas_str = 'environment_humidity'
            log = False
        elif meas == 'ileak_diff':
            plt.suptitle('ileak_nbr - ileak')
            plt.ylabel('Current (A)')
            meas_str = 'strip_ileak_diff'
            log=False
        elif meas == 'rbias_diff':
            plt.suptitle('rbias_nbr - rbias')
            plt.ylabel('Resistance ($\Omega$)')
            meas_str = 'strip_rbias_diff'
            log=False
        if meas_first:
            title = meas_str + '_' + filename
        else:
            title = filename + '_' + meas_str
        plt.savefig('%s.png' %title)
        if log:
            #data_abs = [[strip,abs(meas)] for strip, meas in data]
            data_abs = [abs(meas) for meas in data]
            plt.semilogy(data_abs, '-r.')
            plt.savefig('%s_logy.png' %title)


#This is really annoying but in this version of python dictionaries are unordered
# so the only way to make the output file ordered in a specific way is to manually
# make a list
def Output(sensor, filename, check_diff):
    meas_order = ['strip', 'ileak', 'ileaknbr', 'ileak_diff', 'bias', 'rbias', 'rbiasnbr', 'rbias_diff', 'pinhole', 'coupC', 'interC', 'interR', 'humid', 'airT', 'chuckT']
    if not check_diff:
        meas_order.remove('ileak_diff')
        meas_order.remove('rbias_diff')
    fout = open(filename[:-4] + '_StripMeasurements.txt', 'w')
    for meas in meas_order:
        if sensor.meas_taken()[meas]:
            fout.write(meas+'\t')
    fout.write('\n')
    for strip in sensor.get_strips():
        for meas in meas_order:
            if meas == 'strip':
                fout.write(str(strip[meas])+'\t')
            elif sensor.meas_taken()[meas]:
                fout.write('%.4g' % strip[meas])
                fout.write('\t')
        fout.write('\n')

#checks if you have the pyroot library installed. If you do, it will then output your
# measurements to a ROOT file. You must use the '-r' argument when running
# the script in order to run this function
# I need to do this weird thing with making a list into an array
# becaues pyroot is terrible and has problems making branches
def makeRoot(sensor, filename):
    from array import array
    try:
        import ROOT as R
    except importError:
        print 'pyRoot is not installed'
        return
    tree = R.TTree('meas', 'Measurement Data')
    tree.Branch('strip', array( 'i', sensor.get_meas('strip')), 'strip/I')
    for meas in sensor.meas_taken():
        if not sensor.meas_taken()[meas]: continue
        if meas == 'strip': continue
        tree.Branch(meas, array( 'f', sensor.get_meas(meas)), '%s/F' %meas)
    tree.Fill()
    RFile = R.TFile(filename[:-4] + '_StripMeasurements.root', 'RECREATE')
    RFile.Write("",R.TObject.kOverwrite)
    RFile.Close()

def main():
    args=parser.parse_args()
    sensor = readFile(args.file, args.keep_all)
    if args.reverse:
        sensor.reverse_strips()
    sensor.order()
    sensor.check_measurements()
    if args.check_diff:
        sensor.compare_neighbor('ileak')
        sensor.compare_neighbor('rbias')
    if not args.noplot:
        plotter(sensor, args.file, args.meas_first)
    Output(sensor, args.file, args.check_diff)
    if args.root:
        makeRoot(sensor, args.file)

if __name__ == '__main__':
    main()
    

