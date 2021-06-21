a = [4, 1, 6, 2, 7, 3, 8, 5]
step = len(a)

def crack(text):
    def func(chunk):
        temp = [ chunk[a[i]-1] for i in range(len(chunk))]
        return ''.join(temp)      
    result = ''
    for i in range(0, len(text), step):
        result += func(text[i: i+step])
    print(result)

crack('ETEGENLMDNTNEOORDAHATECOESAHLRMI')