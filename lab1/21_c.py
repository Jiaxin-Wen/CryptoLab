text = "KQEREJEBCPPCJCRKIEACUZBKRVPKRBCIBQCARBJCVFCUPKRIOFKPACUZQEPBKRXPEIIEABDKPBCPFCDCCAFIEABDKPBCPFEQPKAZBKRHAIBKAPCCIBURCCDKDCCJCIDFUIXPAFFERBICZDFKABICBBENEFCUPJCVKABPCYDCCDPKBCOCPERKIVKSCPICBRKIJPKABI"

# result = {}
# for i in range(26):
#     char = chr(ord("A") + i)
#     result[char] = text.count(char) / len(text)

# result = sorted(result.items(), key=lambda x: x[1])
# for i in result[::-1]:
#     print(i)

result = [chr(((ord(i) - ord('A')) * 11 + 8) % 26 + ord('A')).lower() for i in text]
print(''.join(result))