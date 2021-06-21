import itertools
from itertools import chain
from copy import copy
from tqdm import tqdm
from multiprocessing import Pool
from os import cpu_count

class Rotor:
    def __init__(self, setting, trigger, id):
        self.setting = setting
        self.trigger = trigger
        self.offset = None #self.char2id(offset)
        self.id = id
    
    def char2id(self, char):
        return ord(char) - ord('A')
    
    def id2char(self, id):
        return chr(ord('A') +id)

    def forward(self, char, flag):
        new_flag = self.id2char(self.offset) == self.trigger
        if flag: 
            self.offset = (self.offset + 1) % 26

        pos = self.char2id(char)
        let = self.setting[(pos + self.offset) % 26]
        pos = self.char2id(let)
        char = self.id2char((pos - self.offset + 26) % 26)
        
        flag = new_flag
        # print(f'rotor {self.id}, offset = {self.offset}, position = {self.id2char(self.offset)}, input = {ori_char}, output = {char}')
        return char, flag
    
    def backward(self, char):
        pos = self.char2id(char)
        let = self.id2char((pos + self.offset) % 26)
        pos = self.setting.find(let)
        char = self.id2char((pos - self.offset + 26) % 26)
        # print(f'rotor {self.id}, input = {ori_char}, output = {char}')
        return char
    
    def __repr__(self):
        result = {
            "id": self.id,
            "offset": self.offset,
        }
        return repr(result)


class Enigma:
    def __init__(self):
        '''
        rotor settings参照https://www.101computing.net/enigma/js/index.js
        '''
        self.reflector = "YRUHQSLDPXNGOKMIEBFZCWVJAT" # 反射器
        self.all_rotors = [
            Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q", 0),
            Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E", 1),
            Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V", 2),
            Rotor("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J", 3),
            Rotor("VZBRGITYUPSDNHLXAWMJQOFECK", "Z", 4)
        ]
    
        self.keys = None
        self.rotor_ids = None
        self.plug_board = {} # {"O":"U", "U": "O", "D": "Z", "Z": "D", "B":"T", "T": "B"}
    
    def parse_keys(self, keys):
        return [keys % 26, (keys // 26) % 26, (keys // (26**2)) % 26]

    def set_param(self, keys, rotor_ids, plug_board):
        if isinstance(keys, list):
            self.keys = keys
        else:
            self.keys = self.parse_keys(keys)
        self.rotor_ids = rotor_ids
        self.plug_board = {}
        if plug_board is not None:
            for pair in plug_board:
                self.plug_board[pair[0]] = pair[1]
        
        self.rotors = [self.all_rotors[id] for id in self.rotor_ids]
        for key, rotor in zip(self.keys, self.rotors):
                rotor.offset = key

    def restore(self):       
        for key, rotor in zip(self.keys, self.rotors):
            rotor.offset = key
    
    def encrypt(self, char): # 加密一个字符
        char = char.upper()
        flag = True

        for rotor in self.rotors[::-1]:
            char, flag = rotor.forward(char, flag)        

        char = self.reflector[ord(char) - ord('A')]
        for rotor in self.rotors:
            char = rotor.backward(char)
        return char   
    
    def forward(self, step):
        for _ in range(step):
            char, flag = "A", True
            for rotor in self.rotors[::-1]:
                char, flag = rotor.forward(char, flag)
       
    def __call__(self, text, plug=True):
        if plug:
            text = [self.plug_board[i] if i in self.plug_board.keys() else i for i in text]
        text = [self.encrypt(char) for char in text]
        if plug:
            text = [self.plug_board[i] if i in self.plug_board.keys() else i for i in text]
        result = ''.join(text)
        return result


def func(sample):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text = sample['text']
    all_cycles = sample['all_cycles']
    key = sample['key']
    rotor_ids = sample['rotor_ids']
    
    enigma = Enigma()
    enigma.set_param(key, rotor_ids, None) 

    table = [[0 for _ in range(26)] for _ in text]

    for j in range(26):
        enigma.restore()
        for i in range(len(text)):
            table[i][j] = enigma(chr(ord('A') +j), plug=False)

    def check(s, cycle):
        temp = s
        for pos in cycle:
            temp = table[pos][ord(temp) - ord('A')] # 直接取
            # enigma.restore() # 重置offset
            # enigma.forward(pos)
            # temp = enigma(temp, plug=False) # 得到输出
        flag = s == temp
        return flag

    result = []

    all_plug_setting = set() # 环组和环组之间是并集，环组内是交集
    for char, cycles in all_cycles.items(): # 遍历环组
        intra_plug = None
        for cycle in cycles: # 每个环, 只能限制开头字母char的映射
            temp_plug = set()
            for s in alphabet: # char <-> s
                if s == char:
                    continue
                flag = True
                for cycle in cycles:
                    if not check(s, cycle):
                        flag = False
                        break
                if flag:
                    temp_plug.add((char, s))
                    temp_plug.add((s, char))
            if intra_plug is None:
                intra_plug = temp_plug
            else:
                intra_plug &= temp_plug # 环组内取交集
        all_plug_setting |= intra_plug
    if not any(all_plug_setting):
        all_plug_setting = None 
    result = [key, rotor_ids, all_plug_setting]
    return result

class Cracker:
    def __init__(self):
        self.enigma = Enigma()

    def parse(self, ptext, ctext):
        # 不需要check是否有相同字母...

        def dfs(current, end, ids=[]):
            # print(f'current = {current}, end = {end}, ids = {ids}')
            ids = copy(ids)
            ids.append(current)
            char = ctext[current] # 对应的字母
            if char == end: # 找到一个环
                temp.append(ids)
            else:
                next_ids = [i for i, c in enumerate(ptext) if c == char and i not in ids]
                for id in next_ids:
                    dfs(id, end, ids)
            
        result = {} # char = list of list of id
        for i, p in enumerate(ptext):
            temp = []
            dfs(i, p) # list of list of id
            if any(temp):
                if p not in result:
                    result[p] = []
                result[p].extend(temp)
    
        return result
    
    def crack(self, ptext, ctext):
        '''
        从text中得到环
        {char : list of list of id}

        result = []

        遍历rotor的排列: permutation(5, 3)
            遍历rotor的setting: 26*26*26
                遍历环组Cj:（环组：指全部开头结尾相同的环）
                    对于Cj的首尾字母E，遍历S(E):
                        flag = True
                        遍历环组中的每个环 ci,j：
                            if ci,j不满足:
                                flag = False
                                break
                        if flag:
                            result.append([rotor的排列，rotor的setting, 以及插线板的设定E<->S(E)])
                
                filter results 去掉插线板冲突的           
        '''
        all_cycles = self.parse(ptext, ctext)
        # for k, v in all_cycles.items():
        #     print(f"{k}环组: ")
        #     print(v)
        #     print('='*100)
        # print(all_cycles)
        v = set([tuple(sorted(i)) for i in chain(*all_cycles.values())])
        print('len = ', len(v))
        data = []
        for key in (range(26**3)):
            for rotor_ids in list(itertools.permutations(list(range(5)), 3)):
                data.append({
                    "text": ptext,
                    "all_cycles": all_cycles,
                    "key": key,
                    "rotor_ids": rotor_ids
                })
            
        result = []
        with Pool(cpu_count()) as pool:
            iter = pool.imap(func, data)
            for i in tqdm(iter):
                if i[-1] is not None:
                  result.append(i)
        
        print('get result = ', result)
        # print('filter...')
        enigma = Enigma()
        result_dict = {}
        for setting in tqdm(result):
            key, rotor_ids, plug_board = setting[0], setting[1], setting[2]
            enigma.set_param(key, rotor_ids, plug_board) # 设置参数
            # enigma.restore() # 复位生效
            if enigma(ptext) == ctext:
                k = (tuple(enigma.parse_keys(key)), tuple(rotor_ids))
                result_dict[k] = plug_board
        
        if any(result_dict):
            enigma = Enigma()
            for k, v in result_dict.items():
                print('rotor keys = ', k[0])
                print('rotor ids = ', k[1])
                print('plug board = ', v)
                print('='*100)
        else:
            print('crack failed!!')


if __name__ == "__main__":
    # enigma = Enigma()
    # {"O":"U", "U": "O", "D": "Z", "Z": "D", "B":"T", "T": "B"}
    # enigma.set_param([21, 6, 14], [3, 0, 2], [["O", "U"], ["U", "O"], ["D", "Z"], ["Z", "D"], ["T", "B"], ["B", "T"]])
    # ptext = 'TODAYISANICEDAYBUTMYHOMEWORKHASNOTFINISHED'
    # ctext = 'AAVRDVLBXJDMYIVVLWCLUDKSKQSHCUWQTLBVDBQEPO'
    # # TODAY IS A NICE DAY BUT MY HOMEWORK HAS NOT FINISHED
    # # AAVRD VL B XJDM YIV VLW CL UDKSKQSH CUW QTL BVDBQEPO
    # # AAVRD VL B XJDM YIV VLW CL UDKSKQSH CUW QTL BVDBQEPO
    # ctext = enigma(ptext) # XMRGTG
    # print('result = ', ctext)

    ptext = 'TODAYISANICEDAYBUTMYHOMEWORKHASNOTFINISHED'
    ctext = 'AAVRDVLBXJDMYIVVLWCLUDKSKQSHCUWQTLBVDBQEPO'
    cracker = Cracker()
    cracker.crack(ptext, ctext)