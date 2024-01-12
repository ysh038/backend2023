# 채팅 서버

## 실행환경

Python3로 개발

client는 하위 디렉토리의 CHAT_CLIENT 디렉토리에 존재

> python3 server.py --port=포트번호 

형태로 실행

## 클라이언트에서 사용 가능한 명령어

- /help : 사용 가능 명령어를 나열한다.
- /name : 채팅 이름을 지정한다.
- /rooms : 채팅 방 목록을 출력한다.
- /create : 채팅 방을 만든다.
- /join : 채팅 방에 들어간다.
- /leave : 채팅 방을 나간다.
- /shutdown : 채팅 서버를 종료한다.

## 코드 설명

### 전역 변수

``` python
FLAGS = flags.FLAGS

flags.DEFINE_integer(name="worker", default=2, help="워커 스레드 개수")
flags.DEFINE_string(name="ip", default="127.0.0.1", help="서버 IP 주소")
flags.DEFINE_integer(name="port", default=None, required=True, help="서버 port 번호")
```
FLAGS는 서버 실행에 옵션을 줄 수 있도록 한다.

#### 예시
--worker=2 : 스레드 개수 5개로 설정

--port=0000 : 해당 서버 포트번호 0000으로 설정

``` python
# mutex 와 condition variable
m = threading.Lock()
cv = threading.Condition(m)
```

Multi-Threading을 위한 Mutex와 Condition Variable

### 함수

#### main

- 서버 소켓 생성 후 클라이언트의 연결을 대기

- Multi-Threading을 위한 워커 스레드 생성

- 다중 클라이언트 접속을 위한 select 메소드

- 클라이언트가 접근하면 데이터를 JSON형태로 받고, 데이터가 들어왔음을 Condition Variable을 통해 알림

#### consumer_thread

- wait 중이던 cv가 깨어나면 queue에 들어간 작업을 실행한다.

- handler가 클라이언트에게 받은 데이터를 분류해 올바른 함수에게 전달한다.

- consumer_thread는 다시 notify가 올때까지 cv.wait()로 잠든다

#### create_chat_room

- 채팅방을 생성한다. 같은 채팅방 내의 유저끼리만 서로 채팅이 보인다.

- 클라이언트 소켓과 채팅방이름을 Key-Value 형태로 배열에 저장 (채팅방 목록)

- 성공적으로 채팅방이 생성되었음을 send_to_client 함수에게 전달해 클라이언트에게 알린다.

#### join_chat_room

- 이미 존재하는 채팅방에 들어간다.

- 현재 클라이언트 소켓이 chat_rooms에 들어가있나 검사해 없으면 들어간다. (여러 채팅방에 중복 접근 불가)

- 성공적으로 들어갔음을 마찬가지로 클라이언트에게 알린다.

- Key-Value 형태로 생성했던 채팅방배열안에 배열형태로 클라이언트 소켓들이 들어감

#### chang_user_name

- 사용자의 이름을 변경한다. (초기 이름은 소켓 생성시 부여된 id)

#### send_to_others

- 같은 채팅방에 있는 다른 사용자들에게 채팅을 보낸다.

- 본인을 제외한 다른 사용자들에게 BroadCasting 형식으로 보낸다.

#### leave_chat_room

- 채팅방에서 나온다.

- 채팅방안의 클라이언트 소켓 배열에서 pop 시킨다.

#### shut_down_server

- 서버를 종료한다.

- 먼저 클라이언트 소켓들의 연결을 끊는다.

- mutex를 전부 놓는다. thread도 종료

- 서버 닫음

#### show_rooms

- 현재 채팅방의 목록을 보여준다.

#### send_to_client

- 서버에서 클라이언트에게 데이터를 전달할 때 사용하는 함수

- TCP에서 send함수는 일부만 전송되었을 수도 있기때문에 데이터가 모두 전송되지 않았다면 이어서 재전송한다.

```python
# TCP 에서 send() 함수는 일부만 전송될 수도 있다.
# 따라서 보내려는 데이터를 다 못 보낸 경우 재시도 해야된다.
to_send = len(serialized)
to_send_big_endian = int.to_bytes(to_send, byteorder="big", length=2)

# 받는 쪽에서 어디까지 읽어야 되는지 message boundary 를 알 수 있게끔 2byte 길이를 추가한다.
serialized = to_send_big_endian + serialized

# print(f"[C->S:총길이={len(serialized)}바이트] 0x{to_send:04x}(메시지크기) {"+ " + msg_str if msg_str else ""}")
```
#### is_already_join

- 클라이언트가 이미 채팅방에 들어가있는지 판단하는 함수

- 채팅방에서 다른 채팅방을 생성하거나, 채팅방에서 다른 채팅방을 들어가는 경우

## 알게된 점

- 기본적인 python기반 서버 작성법

- select를 통한 I/O multiplexing 구현

- mutex와 condition variable을 통한 비동기처리

- multi-threading