from utils import get_len, cal_ci, get_max_freq
import numpy as np

text = "BNVSNSIHQCEELSSKKYERIFJKXUMBGYKAMQLJTYAVFBKVTDVBPVVRJYYLAOKYMPQSCGDLFSRLLPROYGESEBUUALRWXMMASAZLGLEDFJBZAVVPXWICGJXASCBYEHOSNMULKCEAHTQOKMFLEBKFXLRRFDTZXCIWBJSICBGAWDVYDHAVFJXZIBKCGJIWEAHTTOEWTUHKRQVVRGZBXYIREMMASCSPBHLHJMBLRFFJELHWEYLWISTFVVYEJCMHYUYRUFSFMGESIGRLWALSWMNUHSIMYYITCCQPZSICEHBCCMZFEGVJYOCDEMMPGHVAAUMELCMOEHVLTIPSUYILVGFLMVWDVYDBTHFRAYISYSGKVSUUHYHGGCKTMBLRX"


m = 6

keys = [-1] * m
text_ids = np.array([(ord(i) - ord('A')) for i in text])
result = np.zeros_like(text_ids)

real_max = [ord(x) - ord('A') for x in ['E', 'T', 'A', 'O', 'I', 'N']]
sample_max = [ord(x) - ord('A') for x in get_max_freq(text, m)]

def dfs(id):
    if id == 6:
        temp_text = ''.join([chr(i + ord('A')) for i in result])
        score = cal_ci(temp_text)
        if score < 0.06:
            return 
        else: # 一个可能的key
            print('keys = ', ''.join([chr(i + ord('A')) for i in keys]))
            print('ptext = ', ''.join([chr(i + ord('A')) for i in result]))
            print('='*100)
            return 
    for i in real_max:
        keys[id] = (26 - i + sample_max[id]) % 26
        result[id::m] = (text_ids[id::m] - sample_max[id] + i + 26) % 26
        dfs(id + 1)

dfs(0)