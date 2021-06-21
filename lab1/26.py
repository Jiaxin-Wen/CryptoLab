def decode(text, m, n):
    result = ''
    chunk = m * n
    for j in range(0, len(text), chunk):
        for i in range(n):
            result += text[j: j+chunk][i::n]
    print(result)

decode('myamraruyiqtenctorahroywdsoyeouarrgdernogw', 3, 2)