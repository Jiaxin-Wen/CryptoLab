def crack(text):
    for offset in range(26):
        temp = [chr((ord(i) - ord('A') + offset) % 26 + ord('A')) for i in text]
        print(''.join(temp))


crack('BEEAKFYDJXUQYHYJIQRYHTYJIQFBQDUYJIIKFUHCQD')