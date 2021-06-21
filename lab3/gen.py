from Crypto.Util import number


def generate(flag = True):
    if flag: # 生成一个素数
        prime = number.getPrime(512)
        prime = prime.to_bytes(64, byteorder='little')

        assert prime[-1]>>7 == 1
        assert prime[0]&0x01 == 1

        with open("num.p", 'wb') as f:
            f.write(prime)
    else: # 生成一个非素数
        num = None
        for i in range(1<<511, 1<<512):
            if i % 2 != 0 and not number.isPrime(i):
                num = i
                break
        num = num.to_bytes(64, byteorder='little')
        assert num[-1]>>7 == 1
        assert num[0]&0x01 == 1
        with open("num.n", "wb") as f:
            f.write(num)

generate(flag=False)
generate(flag=True)

# with open("num", "rb") as f:
#     v = f.read(64)
#     a = int.from_bytes(v, byteorder="little")

# print('a = ', a)