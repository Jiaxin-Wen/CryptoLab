import numpy as np

def get_dis(text):
    result = {}
    for i in range(26):
        c = chr(i + ord('A'))
        result[c] = text.count(c) / len(text)
    result = dict(sorted(result.items(), key=lambda x: x[1])[::-1])
    print(result)
    return result


def cal_ci(text):
    if len(text) == 1:
        return 0

    fs = []
    for i in range(26):
        char = chr(ord("A") + i)
        fs.append(text.count(char))
    fs = [i * (i-1) for i in fs]
    n = len(text)
    ci = sum(fs) / (n * (n - 1))
    return ci

def get_len(text):
    result = {}
    for m in range(3, 10):
        temp = []
        
        for i in range(m):
            temp.append(cal_ci(text[i::m]))
        result[m] = temp
        # print('m = ', m)
        # print('ci = ', temp)
        # print('='*100)

    keys = list(result.keys())
    avgs = [np.mean(i) for i in result.values()]
    print('推测m = ', keys[np.argmax(avgs)])


def get_max_freq(text, m):

    def _get_max_freq(text):
        result = []
        for i in range(26):
            result.append(text.count(chr(i + ord('A'))))
        id = np.argmax(result)
        return chr(id + ord('A'))
    
    result = []
    for i in range(m):
        temp = text[i::m]
        result.append(_get_max_freq(temp))

    print('max freq = ', result)
    return result