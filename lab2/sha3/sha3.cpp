/*
sha3-256(M): 

海绵函数: SPONGE[f, pad, r](N, d)
f函数:  Keccak-p置换，256中的超参数设置是Keccak[512](M, 256)
pad: 10*1,  j = (-m-2) mod x
- 24轮
- b = 1600 
  状态(state.lane): 5*5*64 = 1600
- c = 512 // 输出长度的2倍
- r = b - c = 1088
- N = 512 // 输入长度
- d = 256 //输出长度
*/

#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <assert.h>
#include <fstream>
using namespace std;

#define ROUND 24
#define N 64
#define D 32
#define RATE 136

#define ROTL64(x, y) (((x) << (y)) | ((x) >> (64 - (y))))

static const uint64_t iota_constant[24] = {
    0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
    0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
    0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008
};

static const int rot_constant[24] = {
    1,  3,  6,  10, 15, 21, 28, 36, 45, 55, 2,  14,
    27, 41, 56, 8,  25, 43, 62, 18, 39, 61, 20, 44
};

static const int pi_constant[24] = {
    10, 7,  11, 17, 18, 3, 5,  16, 8,  21, 24, 4,
    15, 23, 19, 13, 12, 2, 20, 14, 22, 9,  6,  1
};


static union { //union
    uint64_t lane[25]; //5*5*64bit
    uint8_t bytes[200]; // 1600bit
} state;
int padstart;
int padend;

uint64_t C[5], tmp;
uint8_t md[D];

static void keccak() {
  for(int round = 0 ; round < ROUND; round++){     
    //theta
    for(int i = 0 ; i < 5; i++)
        C[i] = state.lane[i] ^ state.lane[i+5] ^ state.lane[i+10] ^ state.lane[i+15] ^ state.lane[i+20];
    for(int i = 0 ; i < 5; i++){
        tmp = C[(i + 4) % 5] ^ ROTL64(C[(i + 1) % 5], 1);
        for(int j = 0 ; j < 25; j+=5)
            state.lane[i + j] ^= tmp;
    }

    //rho: lane内(z轴)重排
    //pi: lane间重排
    tmp = state.lane[1];
    int tmp_id;
    for(int i = 0 ; i < 24 ; i++){
        tmp_id = pi_constant[i];
        C[0] = state.lane[tmp_id]; // 暂存结果. 下一步直接赋值
        state.lane[tmp_id] = ROTL64(tmp, rot_constant[i]);
        tmp = C[0];
    }
    
    // Chi
    for(int j = 0; j < 25; j += 5){
        for(int i = 0 ; i < 5; i++)
            C[i] = state.lane[i + j];
        for(int i = 0 ; i < 5; i++)
            state.lane[i + j] ^= (~C[(i + 1) % 5]) & C[(i + 2) % 5];
    }

    //iota
    state.lane[0] ^= iota_constant[round];
  }
}


static void absorb(uint8_t* data, int len) {
    int tmp = 0;
    for(int i = 0 ; i < len ; i++) {
        state.bytes[tmp++] ^= data[i];
        if(tmp == RATE){
            keccak(); //f函数作用一次
            tmp = 0;
        }
    }
}   

static void squeeze() {
    memcpy(md, state.bytes, D); // sha3-256, 直接memcpy即可
}


void print(uint8_t* data, int len){
    for(int i = 0 ; i < len; i++){
        printf("%02x", data[i]);
    }
    puts("");
}


void sha256(uint8_t* data, int data_len) {
    double start = clock();
    absorb(data, data_len);
    squeeze();
    double end = clock();
    printf("time cost = %lfs\n", (end - start) / CLOCKS_PER_SEC);
    printf("rate: %lfs Mbps\n", CLOCKS_PER_SEC / (64 * (end- start)));
}


int main(int argc, char** argv){
    //读取输入
    int len = 2048;
    int padded_len = (2048 / RATE + 1) * RATE;
    uint8_t text[padded_len];
    memset(text, 0, padded_len); // 置0
    ifstream fin(argv[1], ios::binary);
    fin.read((char*)text, 2048);
    fin.close();
    text[2048] = 0x06; // padding 0110
    text[padded_len - 1] = 0x80;

    //hash
    sha256(text, padded_len);

    //输出到文件
    ofstream fout("result", ios::binary);
    fout.write((char*)md, 32);
    fout.close();
    return 0;
}