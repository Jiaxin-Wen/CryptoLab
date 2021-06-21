all: aes.cpp
	g++ aes.cpp -o aes -O2

en: 
	make && ./aes plaintext 1 && cmp result ciphertext

de: 
	make && ./aes ciphertext 0 && cmp result plaintext

