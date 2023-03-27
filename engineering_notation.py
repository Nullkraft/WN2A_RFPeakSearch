

class eng_notation():
    def init(self):
        pass
        
    def eng_format(self, x, units: str=''):
        if x >= 1e12:
            return '{:.2f}e12 '.format(x / 1e12) + units
        elif x >= 1e9:
            return '{:.2f}e9 '.format(x / 1e9) + units
        elif x >= 1e6:
            return '{:.2f}e6 '.format(x / 1e6) + units
        elif x >= 1e3:
            return '{:.2f}e3 '.format(x / 1e3) + units
        elif x >= 1e0:
            return '{:.2f} '.format(x) + units
        elif x >= 1e-3:
            return '{:.2f}e-3 '.format(x / 1e-3) + units
        elif x >= 1e-6:
            return '{:.2f}e-6 '.format(x / 1e-6) + units
        elif x >= 1e-9:
            return '{:.2f}e-9 '.format(x / 1e-9) + units
        else:
            return '{:.2f}e-12 '.format(x / 1e-12) + units

if __name__ == '__main__':
    en = eng_notation()
    test_x = 93e-5 * 1e-2
    formatted_x = en.eng_format(test_x)
    print(formatted_x)

