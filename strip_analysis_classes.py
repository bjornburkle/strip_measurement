#!/usr/bin/python2.7

class strip:

    strips = {
            'strip': 0,
            'bias': 0.0,
            'ileak': 0.0,
            'rbias': 0.0,
            'ileaknbr': 0.0,
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
    
    meas_taken = {
            'strip': True,
            'bias': True,
            'ileak': True,
            'rbias': True,
            'ileaknbr': True,
            'rbiasnbr': True,
            'pinhole': True,
            'coupC': True,
            'interC': True,
            'interR': True,
            'humid': True,
            'airT': True,
            'chuckT': True
            }

    strips = []

    def add_strip(self, strip_meas, keep = False):
        if not isinstance(strip_meas, strip):
            print('Trying to append something other than a strip measurement')
            return
        #if keep == False and (strip_old for strip_old in self.strips if strip_old['strip'] == strip_meas['strip']):
        #    _replace_strip(self, strip_meas.get_all_meas())
        print strip_meas.get_meas('strip')
        print strip_meas.get_all_meas()
        self.strips.append(strip_meas.get_all_meas().copy())
        print self.strips[0]['strip']

    def _replace_strip(self, strip_meas):
        self.strips[next((index for (index, strip_old) in enumerate(self) if strip_old['strip'] == strip_meas['strip']), None)] = strip_meas.copy()

    def order(self):
        temp = sorted(self.strips, key=lambda strip_meas: strip_meas['self'])
        self.strips = temp

    def reverse_strips(self):
        total = len(self.strips)
        for strip_meas in self.strips:
            strip_meas['strip'] = total - strip_meas['strip']

    def get_meas_list(self, meas):
        temp_list = []
        if self.meas_taken[meas] == False:
            print meas, 'measurement not taken'
            return
        for strip_meas in self.strips:
            temp_list.append([strip_meas['strip'], strip_meas[meas]])
        temp_list.sort(key=lambda x: x[0])
        return temp_list

    def check_measurements(self):
        if key == []:
            print 'No strip data was parsed'
            return
        for key in self.strips[0]:
            temp = strips.get_meas_list(key)
            if sum(temp[1,:]) == 0:
                self.meas_taken[key] = False

    def get_list(self):
        return self.strips


def main():
    return 0

if __name__ == '__main__':
    main()

