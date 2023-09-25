#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>

#include <iostream>
#include <string>

using namespace std;

int main(){
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s<0) return 1;

    char buf2[65536];
    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(10001);
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");

    while(1){
        string buf;
        // 사용자에게 입력을 받는다
        getline(cin,buf);

        // eof가 입력되었다면, break를 통해 test5.cpp를 종료한다.
        if(cin.eof()){
            break;
        }

        int numBytes = sendto(s, buf.c_str(), buf.length(),
            0, (struct sockaddr *) &sin, sizeof(sin));
        cout << "Sent: " << numBytes << endl;

        memset(&sin, 0, sizeof(sin));
        socklen_t sin_size = sizeof(sin);
        numBytes = recvfrom(s, buf2, sizeof(buf2),0,
            (struct sockaddr *) &sin, &sin_size);
        
        cout << "Received: " << numBytes << endl;
        cout << "From " << inet_ntoa(sin.sin_addr) << endl;
        // NULL 종료 문자 추가, 이는 곧 다음 반복에서의 buf2 문자열의 초기화와 같다. buf2 문자열 끝에 NULL을 집어넣는 것
        // 이를 하지 않는다면, 다음 번 반복 떄 이전 입력값이 buf2에 남아있는다.
        buf2[numBytes] = '\0'; 
        // 입력 받은 문자열 출력
        // 윈도우 환경에서 ppt에서처럼 [1] + Done이 출력되려면 Ctrl+D가 아닌 Ctrl+Z를 눌러야한다.
        cout << "Received string from server: " << buf2 << endl;
    }

    close(s);    
    return 0;
}