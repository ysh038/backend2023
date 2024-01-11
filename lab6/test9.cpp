#include <iostream>
#include <mutex>
#include <thread>

using namespace std;

int sum = 0;
mutex m;
mutex m2;

void f() {
  for (int i = 0; i < 10 * 1000 * 1000; ++i) {
    m.lock();  // mutex 잡기
    m2.lock();
    ++sum;
    m.unlock();  // mutex 풀기
    m2.unlock();
  }
}

int main() {
  thread t(f);
  for (int i = 0; i < 10 * 1000 * 1000; ++i) {
    m2.lock();
    m.lock();  // mutex 잡기
    ++sum;
    m2.unlock();
    m.unlock();  // mutex 풀기
  }
  t.join();
  cout << "Sum: " << sum << endl;
}