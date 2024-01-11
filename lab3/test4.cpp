#include <arpa/inet.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <iostream>
#include <string>

using namespace std;

int main() {
  int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (s < 0) return 1;

  char buf2[65536];
  struct sockaddr_in sin;
  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  // sin.sin_port = htons(10001);
  sin.sin_port = htons(20326);
  sin.sin_addr.s_addr = inet_addr("127.0.0.1");

  string buf = "Hello World";

  int numBytes = sendto(s, buf.c_str(), buf.length(), 0,
                        (struct sockaddr *)&sin, sizeof(sin));
  cout << "Sent: " << numBytes << endl;

  memset(&sin, 0, sizeof(sin));
  socklen_t sin_size = sizeof(sin);
  numBytes =
      recvfrom(s, buf2, sizeof(buf2), 0, (struct sockaddr *)&sin, &sin_size);

  cout << "Received: " << numBytes << endl;
  cout << "From " << inet_ntoa(sin.sin_addr) << endl;
  // 받은 문자열 출력
  cout << "Received from server: " << buf2 << endl;

  close(s);
  return 0;
}