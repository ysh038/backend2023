#include <arpa/inet.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include <iostream>

using namespace std;

int main() {
  int s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  if (s < 0) {
    cerr << "socket() failed: " << strerror(errno) << endl;
    return 1;
  }

  /* 연결 */
  struct sockaddr_in sin;
  memset(&sin, 0, sizeof(sin));  // 이 경우에는 안해도 되긴 함
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = inet_addr("127.0.0.1");
  sin.sin_port = htons(10001);
  if (connect(s, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
    cerr << "connect() failed: " << strerror(errno) << endl;
    return 1;
  }

  char buf[60 * 1024];
  int r = send(s, buf, sizeof(buf), 0);
  if (r < 0) {
    cerr << "send() failed: " << strerror(errno) << endl;
  } else {
    cout << "Sent: " << r << "bytes" << endl;
  }

  /* 다시 데이터를 받는 부분 */
  r = recv(s, buf, sizeof(buf), 0);
  if (r < 0) {
    cerr << "recv() failed: " << strerror(errno) << endl;
  } else {
    cout << "Receiced: " << r << "bytes" << endl;
  }

  /* 한번 더 다시 데이터를 받는 부분 */
  r = recv(s, buf, sizeof(buf), 0);
  if (r < 0) {
    cerr << "recv() failed: " << strerror(errno) << endl;
  } else if (r == 0) {
    cout << "Socket closed" << endl;
  } else {
    cout << "Receiced: " << r << "bytes" << endl;
  }

  close(s);
  return 0;
}