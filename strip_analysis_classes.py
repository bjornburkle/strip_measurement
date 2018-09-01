import numpy as np

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

    def __init(self):
        return self

    #def __init__(self, num):
    #    self.strips['strip'] = num


    def add_meas(self, meas, value):
        self.strips[meas] = value

    def get(self, meas):
        return self.strips['meas']
    
    def clear(self):
        for key in self:
            if key == 'strip':
                strips[key] = 0
            else:
                strips[key] = 0.0

class sensor:
    
    meas_taken = {
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

    def __init__(self):
        self = []

    def add_strip(self, strip_meas, keep = False):
        if type(strip_meas) != strip:
            print('Trying to append something other than a strip measurement')
            return
        if keep == False and (strip for strip in self if strip['strip'] == strip_meas['strip']):
            _replace_strip(self, strip_meas)
        self.append(strip_meas)

    def _replace_strip(self, strip_meas):
        self[next((index for (index, strip) in enumerate(strip) if strip['strip'] == strip_meas['strip']), None)] = strip_meas

    def order(self):
        temp = sorted(self, key=lambda strip: strip['self'])
        self = temp

    def reverse_strips(self):
        total = len(self)
        for strip in self:
            strip['strip'] = total - strip['self']

    def get_meas_list(self, meas):
        temp_list = []
        for strip in self:
            temp_list.append(strip['strip'], strip[meas])
        temp_list.sort(key=lambda x: x[0])
        self = temp_list

    def check_measurements(self):
        if key = []:
            print 'No strip data was parsed'
            return
        for key in self[0]:
            temp = self.get_meas_list(key)
            if sum(temp[1,:]) == 0:
                meas_taken[key] = False


def main():
    return 0

if __name__ == '__main__':
    main()

