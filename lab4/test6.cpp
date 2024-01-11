#include <arpa/inet.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <fstream>
#include <iostream>
#include <string>

#include "person.pb.h"

using namespace std;
using namespace mju;

int main() {
  // 소켓
  int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (s < 0) return 1;

  char s2[65536];

  struct sockaddr_in sin;
  memset(&sin, 0, sizeof(sin));
  sin.sin_family = AF_INET;
  // sin.sin_port = htons(10001);
  sin.sin_port = htons(20326);
  sin.sin_addr.s_addr = inet_addr("127.0.0.1");

  // Person 객체
  Person *p = new Person;
  p->set_name("SH Yoo");
  p->set_id(60172174);

  Person::PhoneNumber *phone = p->add_phones();
  phone->set_number("010-111-1234");
  phone->set_type(Person::MOBILE);

  phone = p->add_phones();
  phone->set_number("02-100-1000");
  phone->set_type(Person::HOME);

  const string s1 = p->SerializeAsString();

  int numBytes = sendto(s, s1.c_str(), s1.length(), 0, (struct sockaddr *)&sin,
                        sizeof(sin));
  cout << "Sent: " << numBytes << endl;

  memset(&sin, 0, sizeof(sin));
  socklen_t sin_size = sizeof(sin);
  numBytes = recvfrom(s, s2, sizeof(s2), 0, (struct sockaddr *)&sin, &sin_size);

  cout << "Received: " << numBytes << endl;
  cout << "From " << inet_ntoa(sin.sin_addr) << endl;
  // 받은 데이터 출력
  cout << "Received from server: " << s2 << endl;

  cout << "Length:" << sizeof(s2) << endl;
  cout << s2 << endl;

  Person *p2 = new Person;
  p2->ParseFromString(s2);
  cout << "Name:" << p2->name() << endl;
  cout << "ID:" << p2->id() << endl;
  for (int i = 0; i < p2->phones_size(); ++i) {
    cout << "Type:" << p2->phones(i).type() << endl;
    cout << "Phone:" << p2->phones(i).number() << endl;
  }

  close(s);
}