text =  "EMGLOSUDCGDNCUSWYSFHNSFCYKDPUMLWGYICOXYSIPJCKQPKUGKMGOLICGINCGACKSNISACYKZSCKXECJCKSHYSXCGOIDPKZCNKSHICGIWYGKKGKGOLDSILKGOIUSIGLEDSPWZUGFZCCNDGYYSFUSZCNXEOJNCGYEOWEUPXEZGACGNFGLKNSACIGOIYCKXCJUCIUZCFZCCNDGYYSFEUEKUZCSOCFZCCNCIACZEJNCSHFZEJZEGMXCYHCJUMGKUCY"

keymap = {'F': 'w', 'C':'e', 'Z':'h', 'N':'l', 'U':'t', 'S':'o', 'O':'n', 'X':'p', 'Y':'r', 'I':'d', 'G':'a', 'D':'b', 'W':'g', 'K':'s', 'L':'y', 'M':'m', 'A':'v', 'H':'f', 'P':'u', 'J':'c', 'E':'i', 'Q':'j'}
def preprocess(text):
    for k, v in keymap.items():
        text = text.replace(k, v)  
        # text = text.replace(k , v+'-')
    return text

keys = [i.upper() for i in keymap.values()]
left = []
for i in range(26):
    c = chr(ord("A") + i)
    if c not in keys:
        left.append(c)
print('剩余字母: ', left)
    
text = preprocess(text)
print(text)

result = {}
for i in range(26):
    char = chr(ord("A") + i)
    result[char] = text.count(char) / len(text)

result = sorted(result.items(), key=lambda x: x[1])
for i in result[::-1]:
    print(i)