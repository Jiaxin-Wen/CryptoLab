all: rc4.cpp
	g++ rc4.cpp -o rc4 -O2

en:
	make && ./rc4 plaintext && cmp result ciphertext

de: 
	make && ./rc4 ciphertext && cmp result plaintext