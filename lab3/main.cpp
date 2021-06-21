/*
miller-rabin算法实现
*/

#include <stdint.h>
#include <fstream>
#include <iostream>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
using namespace std;

#define SIZE 16
#define N 128
#define MAX 0x100000000 //按无符号数

class BigInt
{
public:
    uint64_t data[N]; //用64存32的值, 64保证中间计算不溢出
    int len; 

    BigInt(){
        memset(data, 0, sizeof(data)); //默认值为0
        len = 1;
    }

    BigInt(int* _data){ //初始化N
        memset(data, 0, sizeof(data));
        for(int i = 0 ; i < SIZE ; i++)
            memcpy(&data[i], &_data[i], 4); //copy4个bytes
        setlen();
    }
    
    BigInt(int v){
        memset(data, 0, sizeof(data));
        data[0] = v;
        len = 1;
    }

    inline void setlen() {
        for(len = N; len > 1 && data[len - 1] == 0; --len);
    }

    inline bool operator < (const BigInt& other) const {
        if(len != other.len)
            return len < other.len;
        for(int i = len - 1; i >= 0; i--){
            if(data[i] != other.data[i])
                return data[i] < other.data[i];
        }
        return false; //相等
    }

    inline bool operator >= (const BigInt& other) const {
        if(len != other.len)
            return len > other.len;
        for(int i = len - 1; i >= 0; i--){
            if(data[i] != other.data[i])
                return data[i] > other.data[i];
        }
        return true; //相等
    }

    inline bool operator == (const BigInt& other) const {
        if(len != other.len)
            return false;

        for(int i = 0; i < len; i++){
            if(data[i] != other.data[i])
                return false;
        }
        return true;
    }

    inline bool operator != (const BigInt& other) const { 
        if(len != other.len)
            return true;

        for(int i = 0 ; i < len ; i++){
            if(data[i] != other.data[i])
                return true;
        }
        return false;
    }

    BigInt operator * (const BigInt& other) const {

        BigInt res;
        for(int i = 0; i < len; i++)
            for(int j = 0 ; j < other.len && i + j < N; j++){
                res.data[i + j] += data[i] * other.data[j]; //结果保存到64位
                if(res.data[i + j] >= MAX) { //防止溢出, 就地检查进位
                if(i + j < N - 1)
                    res.data[i + j + 1] += res.data[i + j] / MAX; //进位
                res.data[i + j] %= MAX;
            }
            }
        res.setlen();
        return res;
    }

    BigInt operator + (const BigInt& other) const {

        BigInt res;
        for(int i = 0; i < len || i < other.len; i++){
            res.data[i] += data[i] + other.data[i];
            if(res.data[i] >= MAX){ 
                res.data[i] -= MAX;
                res.data[i + 1]++;
            }
            assert(res.data[i] < MAX);

        }
        res.setlen();
        return res;
    }

    BigInt operator - (const BigInt& other) const {
        BigInt res;
        for(int i = 0 ; i < N; i++){
            res.data[i] += data[i] - other.data[i];
            if(((res.data[i])>>32) != 0){ //改成unsigned long long防止乘法溢出
                res.data[i] += MAX;
                if (i + 1 < N)
                    res.data[i+1]--;
            }
            assert(res.data[i] < MAX);
        }
        res.setlen();
        return res;
    }

    BigInt& operator -- () {
        if(((--data[0])>>32)!=0){
            for(int i = 0 ; i < N && ((data[i]>>32)!=0); i++){
                data[i] += MAX; //借位
                if(i + 1 < N)
                    data[i + 1]--;
            }
        }
        setlen();
        return *this;
    }

    BigInt& operator ++ () {
        if(++data[0] >= MAX) {
            for(int i = 0 ; i < N && data[i] >= MAX; i++){
                data[i] -= MAX; //进位
                if(i + 1 < N)
                    data[i + 1]++;
                    
            }
        }
        setlen();
        return *this;
    }

    friend void _func(const BigInt& a, const BigInt& b, BigInt& div, BigInt& mod){
        //计算 a / b
        
        BigInt kb[513]; //b * (2 ** k)
        BigInt index[513];
        BigInt bg2(2);
        kb[0] = b;
        index[0] = BigInt(1);
        int size = 1;
        for(; size < 513; size++){
            kb[size] = kb[size - 1] * bg2;
            index[size] = index[size - 1] * bg2;
            if(kb[size] < kb[size - 1]) //溢出
            {   
                size--; 
                break;
            }
        }

        BigInt tmp = a;
        bool flag = false;
        int last_id = size - 1;
        while(!flag){
            flag = true;
            for(int i = last_id; i >= 0; i--){
                if(tmp >= kb[i]) {
                    tmp = tmp - kb[i];
                    div = div + index[i];
                    last_id = i;
                    flag = false;
                    break;
                }
            }
        }
        
        BigInt a_ = a;
        BigInt b_ = b;
        mod = a - (b * div);
        div.setlen();
        mod.setlen();
    }

    BigInt operator % (const BigInt& b) const {
        BigInt div, mod;
        _func(*this, b, div,mod);
        return mod;
    }

    BigInt operator / (const BigInt& b) const {
        BigInt div, mod;
        _func(*this, b, div, mod);
        return div;
    }

    friend BigInt power(BigInt& a, BigInt& b, BigInt& c){
        BigInt res(1);
        BigInt bg1(1);
        BigInt cnt = b;

        BigInt item = a % c;

        // 快速幂
        for(int i = 0 ; i < b.len; i++){
            for(int j = 0 ; j < 32; j++){
                if((b.data[i] >> j) & 1){
                    res = (res * item) % c;
                }
                item = (item * item) % c;
            }
        }
        return res;
    }

    friend BigInt _power(BigInt& a, BigInt& b){
        // a ** b / p 
        BigInt res(a);
        BigInt bg1(1);
        BigInt cnt = b;
        if(cnt == BigInt(0)){
            return bg1;
        }

        while(cnt != bg1){
            res = res * a;
            --cnt;
        }
        return res;
    }

    bool check(){
        return !(data[0] % 2);
    }

    void show(){
        for(int i = len - 1; i >= 0; i--){
            cout<<data[i];
            if(i != 0)
                cout<<",";
        }
        cout<<endl;
    }
};


bool miller_rabin(int* value){
    BigInt p(value);
    BigInt bg0(0);
    BigInt bg1(1);
    BigInt bg2(2);
    BigInt bg3 = p - bg1; // p - 1
    BigInt bg4 = p - bg2; // p - 2
    
    // m * (2 ^ k) 
    // k: 0的个数
    BigInt m = bg3;
    BigInt k(0);

    unsigned long long i = 0;
    while(m.check()){
        ++k;
        m = m / bg2;
    }

    BigInt a = BigInt(rand()) % bg4;
    if(a < bg2)
        a = bg2;
    BigInt x = power(a, m, p);
    if(x == bg1 or x == bg3)
        return true;

    while(k!=0){
        x = power(x, bg2, p);
        if(x == bg1)
            return false;
        if(x == bg3)
            return true;
        --k;
    }

    return false;
}


bool check(int* num, int round){
    for(int i = 0; i < round; i++){
        cout<<"round = "<<i<<endl;
        if(!miller_rabin(num))
            return false;
    }
    return true;
}



int main(int args, char** argv){
    //读取输入
    int len = 64; //64 byte
    int num[SIZE];
    ifstream fin(argv[1], ios::binary);
    fin.read((char*)num, 64);
    fin.close();
    bool flag = check(num, 10); //重复10个随机数
    cout<<"is prime: "<<flag<<endl;

    return 0;
}