#include <fstream>
#include <iostream>
#include <time.h>

using namespace std;

uint8_t S[256];
uint8_t key[128];
uint8_t allkey[2048]; //与明文同等长度的秘钥流

static void init(){
    ifstream fin("key", ios::binary);
    fin.read((char *)key, 128);
    fin.close();
    for(int i = 0 ; i < 256 ; i++){ //初始化S盒
        S[i] = i;
    }
    for(int i = 0, j = 0; i < 256; i++){ //用秘钥打乱S盒
        j = (j + S[i] + key[i % 128]) % 256;
        swap(S[i], S[j]);
    }
}

static void PRGA(){ //PRGA：用S盒生成秘钥流
    int j = 0, k = 0;
    for(int i = 0 ; i < 2048 ; i++){
        j = (j + 1) % 256;
        k = (k + S[j]) % 256;
        swap(S[j], S[k]);
        allkey[i] = S[(S[j] + S[k]) % 256];
    }
}

int main(int argc, char **argv){
    init();
    PRGA();
    uint8_t text[2048];
    ifstream fin(argv[1], ios::binary);
    fin.read((char*)text, 2048);
    fin.close();
    
    double start = clock();
    for(int i = 0 ; i < 2048; i++)
        text[i] = text[i] ^ allkey[i];
    double end = clock();
    printf("time cost = %lfs\n", (end - start) / CLOCKS_PER_SEC);
    printf("rate: %lfs Mbps\n", CLOCKS_PER_SEC / (64 * (end- start)));
    
    ofstream fout("result", ios::binary);
    fout.write((char*)text, 2048);
    fout.close();

    ofstream fout_key("keystream", ios::binary);
    fout_key.write((char*)allkey, 2048);
    fout_key.close();
    
    return 0;
}

