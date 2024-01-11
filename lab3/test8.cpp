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

  struct sockaddr_in sin;

  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  sin.sin_addr.s_addr = INADDR_ANY;
  sin.sin_port = htons(20000 + /*자기서브넷숫자*/ 326);
  if (bind(s, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
    cerr << strerror(errno) << endl;
    return 0;
  }

  // memset(&sin, 0, sizeof(sin));
  // sin.sin_family = AF_INET;
  // sin.sin_port = htons(10001);
  // sin.sin_addr.s_addr = inet_addr("127.0.0.1");

  while (1) {
    char buf2[65536];
    memset(&sin, 0, sizeof(sin));
    socklen_t sin_size = sizeof(sin);
    int numBytes =
        recvfrom(s, buf2, sizeof(buf2), 0, (struct sockaddr *)&sin, &sin_size);

    cout << "Received numBytes: " << numBytes << endl;
    cout << "From " << inet_ntoa(sin.sin_addr) << endl;
    cout << "Received string from client: " << buf2 << endl;

    sendto(s, buf2, strlen(buf2), 0, (struct sockaddr *)&sin, sizeof(sin));

    memset(buf2, 0, sizeof(buf2));
  }
  close(s);
  return 0;
}