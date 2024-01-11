#include <iostream>
#include <mutex>
#include <thread>

using namespace std;

int sum = 0;
mutex m;  // 경합하는 모든 쓰레드 동일한 mutex 사용해야함

void f() {
  for (int i = 0; i < 10 * 1000 * 1000; ++i) {
    // m.lock(); // mutex 잡기
    // ++sum;
    // m.unlock(); // mutex 풀기

    unique_lock<mutex> ul(m);  // mutex 자동으로 풂
    ++sum;
  }
}

int main() {
  thread t(f);
  for (int i = 0; i < 10 * 1000 * 1000; ++i) {
    // m.lock(); // mutex 잡기
    // ++sum;
    // m.unlock(); // mutex 풀기

    unique_lock<mutex> ul(m);  // mutex 자동으로 풂
    ++sum;
  }
  t.join();
  cout << "Sum: " << sum << endl;
}