

class engineering_notation():
    def init(self):
        pass
        
    def eng_format(self, x):
        if x >= 1e12:
            return '{:.2f}T'.format(x / 1e12)
        elif x >= 1e9:
            return '{:.2f}G'.format(x / 1e9)
        elif x >= 1e6:
            return '{:.2f}M'.format(x / 1e6)
        elif x >= 1e3:
            return '{:.2f}k'.format(x / 1e3)
        elif x >= 1e0:
            return '{:.2f}'.format(x)
        elif x >= 1e-3:
            return '{:.2f}m'.format(x / 1e-3)
        elif x >= 1e-6:
            return '{:.2f}u'.format(x / 1e-6)
        elif x >= 1e-9:
            return '{:.2f}n'.format(x / 1e-9)
        else:
            return '{:.2f}p'.format(x / 1e-12)

if __name__ == '__main__':
    en = engineering_notation()
    test_x = 93e-5 * 1e-2
    formatted_x = en.eng_format(test_x)
    print(formatted_x)

