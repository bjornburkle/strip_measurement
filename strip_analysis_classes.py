#!/usr/bin/python2.7

class strip:

    # unfortunately these key names are hard coded into the other scripts
    # which use this file. You are welcome to add keys to this dictionary.
    # But, under no circumstance should you edit any key names unless
    # you want to give yourself a headache. That being said, you are free
    # to change the order. Changing the order should also change the
    # way in which the measurements are ordered in the output text file

    strips = {
            'strip': 0,
            'ileak': 0.0,
            'ileaknbr': 0.0,
            'bias': 0.0,
            'rbias': 0.0,
            'rbiasnbr': 0.0,
            'pinhole': 0.0,
            'coupC': 0.0,
            'interC': 0.0,
            'interR': 0.0,
            'humid': 0.0,
            'airT': 0.0,
            'chuckT': 0.0
            }

    def add_meas(self, meas, value):
        self.strips[meas] = value

    def get_meas(self, meas):
        return self.strips[meas]

    def get_all_meas(self):
        return self.strips
    
    def clear(self):
        for key in self.strips:
            if key == 'strip':
                self.strips[key] = 0
            else:
                self.strips[key] = 0.0


class sensor:

    #the fact that I sometimes use strip as a variable and 
    #sometimes use it when refering to the previous class is
    #pretty bad....sorry about that
    
    _meas_taken = {}
    strips = []

    # takes the measurements contained in the strip class and appends them
    # to the sensor object

    def add_strip(self, strip_meas, keep = False):
        if not isinstance(strip_meas, strip):
            print('Trying to append something other than a strip measurement')
            return
        self.strips.append(strip_meas.get_all_meas().copy())

    # replace a measurement with a new one taken on the same strip
    # note that this is meant to be private so it doesn't check if the strip
    # was measured in the first place, so don't call this in your script
    # instead use self.add_strip(meas, True)

    def _replace_strip(self, strip_meas):
        self.strips[next((index for (index, strip_old) in enumerate(self) if strip_old['strip'] == strip_meas['strip']), None)] = strip_meas.copy()

    #returns the strips member

    def get_strips(self):
        return self.strips


    #rearrange the strips so they are in numerical order

    def order(self):
        if self.strips == []:
            print 'No strip data parsed'
            return
        temp = sorted(self.strips, key=lambda strip_meas:strip_meas['strip'])
        self.strips = temp

    #reverse the strip number
    # useful if you started a measurement at the final strip instead of the
    # first. Adds 1 so it starts at strip number 1

    def reverse_strips(self):
        total = len(self.strips)
        for strip_meas in self.strips:
            strip_meas['strip'] = total - strip_meas['strip'] + 1

    #returns the list of a measurement and its strip number
    # the elements in this list are automatically sorted by strip number

    def get_meas_list(self, meas):
        if self.strips == []:
            print 'No stip data was parsed'
            return
        temp_list = []
        if meas not in self._meas_taken:
            print meas, 'measurement not taken'
            return
        if self._meas_taken[meas] == False:
            print meas, 'measurement not taken'
            return
        for strip_meas in self.strips:
            temp_list.append([strip_meas['strip'], strip_meas[meas]])
        temp_list.sort(key=lambda x: x[0])
        return temp_list

    #returns the meas_taken dictionary
    def meas_taken(self):
        return self._meas_taken

    #returns a list of just one type of measurement
    # this function does not include the strip number and it does
    # not sort the measurement list

    def get_meas(self, meas):
        if self.strips == []:
            print 'No strip data was parsed'
            return
        temp_list = []
        if meas in self._meas_taken and self._meas_taken[meas] == False:
            print meas, 'measurement not taken'
            return
        for strip_meas in self.strips:
            temp_list.append(strip_meas[meas])
        return temp_list

    #checks to see if a certain measurement was taken or not
    # then creates a list saying whether or not they were taken
    # this was made so the keys from the strip class are not
    # hard corded into the corresponding library. Hooray!

    def check_measurements(self):
        if self.strips == []:
            print 'No strip data was parsed'
            return
        for meas in self.strips[0]:
            temp = [strip[meas] for strip in self.strips]
            if sum(temp) == 0:
                self._meas_taken[meas] = False
            else:
                self._meas_taken[meas] = True

    # returns whether or not a specific measurement was taken
    
    def meas_taken(self):
        return self._meas_taken

    # returns the list containing all of the strip measurements
    def get_list(self):
        return self.strips

    # Give script a measurement that you take on the DC pad and DC neighbor pad
    # then create new list which is the difference between the nominal and neighbor value
    # this is then inserted into each "strip" as a new measurement. Make sure that
    # the strips are sorted before running this command
    def compare_neighbor(self, meas):
        assert (self._meas_taken[meas] and self._meas_taken[meas+'nbr']), 'Either %s or %snbr measurement not taken' % (meas, meas)
        meas_str = meas + '_diff'
        new_meas = [ (x - y) for x, y in zip(self.get_meas(meas+'nbr')[:-1], self.get_meas(meas)[1:])]
        new_meas.insert(0, 0.)
        for strip, diff in enumerate(new_meas):
            self.strips[strip][meas_str] = diff
        self._meas_taken[meas_str] = True



def main():
    return 0

if __name__ == '__main__':
    main()

