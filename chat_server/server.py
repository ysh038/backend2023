import socket
import select
import json
import sys
import threading
import time
import queue
# from multiprocessing.dummy import Pool as ThreadPool
from absl import app, flags

FLAGS = flags.FLAGS

flags.DEFINE_integer(name="worker", default=2, help="워커 스레드 개수")
flags.DEFINE_string(name="ip", default="127.0.0.1", help="서버 IP 주소")
flags.DEFINE_integer(name="port", default=None, required=True, help="서버 port 번호")
# flags.DEFINE_enum(name="format", default="json", enum_values=["json", "protobuf"], help="메시지 포맷")

# 클라이언트 소켓을 관리하기 위한 리스트
client_sockets = []

# 채팅방을 저장할 리스트
chat_rooms = []

# 유저 소켓정보와 이름을 저장할 딕셔너리 리스트
users = []

# producer가 작업을 집어넣을 큐 또는 consumer가 작업을 빼내올 큐
queue = []

is_while = True

# mutex 와 condition variable
m = threading.Lock()
cv = threading.Condition(m)

# roomId 배정 정수형 변수
room_count = 1

# 채팅방이름과 소켓을 Key
def create_chat_room(sock,json_data,server_sock):
    # 사용하지 않는 서버 소켓

    title = json_data["title"]

    is_create = True
    if is_already_join(sock,is_create):
        return 0
    else:
        global room_count
        chat_room_group = []
        chat_room = []
        # chat_room 의 인덱스0 = 소켓, 인덱스1 = title
        chat_room.append(sock)
        chat_room.append(title)
        chat_room_group.append(chat_room)
        chat_rooms.append({room_count:chat_room_group})
        print(f"[채팅방 생성] roomId는 {room_count}")

        room_count += 1

        # if FLAGS.format == "json":
        msg = {
            "type" : "SCSystemMessage",
            "text" : "[" + title + "] 방에 입장했습니다."
        }
        send_to_client(sock,msg,sock)

        # chat_rooms에서 특정 sock 찾기 (이후 채팅방 나가기, 삭제 위해 미리 구현)
        # socket_to_delete = sock
        # socket_index = 0
        # for find_room in chat_rooms:
        #     if sock in find_room:
        #         socket_index = chat_rooms.index(find_room)
        #         del find_room[socket_to_delete]
        #         del chat_rooms[socket_index]

def join_chat_room(sock, json_data,server_sock):
    # 사용하지 않는 server_sock

    roomId = json_data["roomId"]

    # 현재 클라이언트 소켓이 chat_rooms에 있나 검사
    is_create = False
    if is_already_join(sock,is_create) == True:
        return 0
    
    # 아무 채팅방도 들어가있지 않다면 join
    global room_count
    chat_room = []
    for room in chat_rooms:
        if roomId in room:
            chat_room.append(sock)
            # title append
            chat_room.append(room[roomId][0][1])
            room[roomId].append(chat_room)
            msg = {
                "type" : "SCSystemMessage",
                "text" : "[" + room[roomId][0][1] + "] 방에 입장했습니다."
            }
            send_to_client(sock,msg,sock)

    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])
    index = 0
    for find_room in chat_rooms:
        if key_list[index] in find_room:
            # 채팅방안에 있는 소켓들 돌면서 sock과 일치하나 확인
            for i in find_room[key_list[index]]:
                if sock in i:
                    send_users = find_room[key_list[index]]
        index+=1
    send_user_sockets = []
    for send_user in send_users:
        send_user_sockets.append(send_user[0])

    user_name = ""

    for user in users:
        if sock in user:
            user_name = user[sock]

    msg = {
        "type" : "SCSystemMessage",
        "text" : f"[{user_name}]님이 방에 입장했습니다."
    }
    
    for send_user_socket in send_user_sockets:
        if sock != send_user_socket:
            send_to_client(send_user_socket,msg,sock)


def change_user_name(sock, json_data, server_sock):
    # 사용하지 않는 server_sock

    new_name = json_data["name"]
    send_users = []
    old_name = ""
    for user in users:
        if sock in user:
            old_name = user[sock]
            user[sock] = new_name
        # # if FLAGS.format == "json":
        msg = {
            "type" : "SCSystemMessage",
            "text" : f"{old_name} 유저의 이름이 {new_name}으로 변경되었습니다."
        }
    send_to_client(sock,msg,sock)

    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])
    index = 0
    for find_room in chat_rooms:
        if key_list[index] in find_room:
            # 채팅방안에 있는 소켓들 돌면서 sock과 일치하나 확인
            for i in find_room[key_list[index]]:
                if sock in i:
                    send_users = find_room[key_list[index]]
        index+=1
    send_user_sockets = []
    for send_user in send_users:
        send_user_sockets.append(send_user[0])

    for send_user_socket in send_user_sockets:
        if sock != send_user_socket:
            send_to_client(send_user_socket,msg,sock)

def send_to_others(sock, json_data,server_sock):
    # 사용하지 않는 server_sock

    # 채팅을 보낼 유저
    send_users = []

    for user in users:
        if sock in user:
            send_user_name = user[sock]

    msg = {
        "type" : "SCChat",
        "member" : send_user_name,
        "text" : json_data["text"]
    }

    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])
    index = 0
    is_find = False

    for find_room in chat_rooms:
        if key_list[index] in find_room:
            # 채팅방안에 있는 소켓들 돌면서 sock과 일치하나 확인
            for i in find_room[key_list[index]]:
                if sock in i:
                    send_users = find_room[key_list[index]]
                    is_find = True
        index+=1
    if is_find == False:
        msg = {
            "type" : "SCSystemMessage",
            "text" : "현재 대화방에 들어가 있지 않습니다."
        }
        send_to_client(sock,msg,sock)
        return 0
    send_user_sockets = []
    for send_user in send_users:
        send_user_sockets.append(send_user[0])

    for send_user_socket in send_user_sockets:
        if sock != send_user_socket:
            send_to_client(send_user_socket,msg,sock)

def leave_chat_room(sock,json_data,sever_sock):
    # 사용하지 않는 json_data, server_sock

    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])
    index = 0

    for find_room in chat_rooms:
        if key_list[index] in find_room:
            # 채팅방안에 있는 소켓들 돌면서 sock과 일치하나 확인
            for i in find_room[key_list[index]]:
                if sock in i:
                    send_users = find_room[key_list[index]]
        index+=1
    send_user_sockets = []
    for send_user in send_users:
        send_user_sockets.append(send_user[0])

    user_name = ""

    for user in users:
        if sock in user:
            user_name = user[sock]

    msg = {
        "type" : "SCSystemMessage",
        "text" : f"[{user_name}]님이 퇴장장했습니다."
    }
    
    for send_user_socket in send_user_sockets:
        if sock != send_user_socket:
            send_to_client(send_user_socket,msg,sock)
            
    index = 0
    # 현재 클라이언트 소켓이 chat_rooms에 있나 검사
    # 채팅방들의 딕셔너리 key값으로 돌면서 검사
    for find_room in chat_rooms:
        if key_list[index] in find_room:
            # 채팅방안에 있는 소켓들 돌면서 sock과 일치하나 확인
            for i in find_room[key_list[index]]:
                if sock in i:
                    # sock 소켓의 인덱스 할당
                    for j in range(len(find_room[key_list[index]])):
                        # 지금 이상한게 leave됨
                        if sock in find_room[key_list[index]][j]:
                            socket_index = find_room[key_list[index]][j].index(sock)
                            title = find_room[key_list[index]][j][1]
                            # 채팅방에서 sock 삭제
                            del find_room[key_list[index]][j] 
                            msg = {
                                "type" : "SCSystemMessage",
                                "text" : f"[{title}]대화 방에서 퇴장했습니다."
                            }
                            send_to_client(sock,msg,sock)

                            # 채팅방이 비었다면 채팅방 폭파
                            if len(find_room[key_list[index]]) == 0:
                                print(f"{title}채팅방은 User가 없어 폭파")
                                # 채팅방 딕셔너리삭제
                                del find_room[key_list[index]]
                                # 채팅방 빈 딕셔너리 삭제
                                del chat_rooms[chat_rooms.index(find_room)]
                                msg = {
                                    "type" : "SCSystemMessage",
                                    "text" : title+"채팅방 폭파!"
                                }
                                send_to_client(sock,msg,sock)
                            return 0
        index+=1
    msg = {
        "type" : "SCSystemMessage",
        "text" : "유저가 채팅방에 들어가있지 않습니다."
    }
    send_to_client(sock,msg,sock)
    return 0

def shutdown_server(sock, json_data, server_socket):
    global is_while
    # 사용하지 않는 sock, json_data
    # 모든 클라이언트의 연결을 끊음
    # 여기에 데이터 처리 로직을 추가합니다.
    # 모든 클라이언트 연결을 종료하는 조건

    # 모든 클라이언트 소켓 종료
    for client_sock in client_sockets:
        if client_sock != server_socket:
                msg = {
                    "type" : "SCSystemMessage",
                    "text" : "서버가 종료됩니다."
                }
                send_to_client(client_sock,msg,sock)
                client_sock.close()
    sock.close()
    server_socket.close()
    is_while = False

    print("서버와 모든 클라이언트 연결을 종료합니다.")

    # 프로그램 종료
    sys.exit()

def show_rooms(sock,json_data, server_socket):
    # 사용하지 않는 json_data, server_socket
    # if FLAGS.format == "json":
    msg = {
        "type" : "SCRoomsResult"
    }

    msg["rooms"] = []
    roomId = []
    room_title = []
    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])

    index = 0

    for chat_room in chat_rooms:
        user_in_room = []
        roomId = key_list[index]
        room_title = chat_room[key_list[index]][0][1]
        for user in users:
            # 채팅방 내 사용자의 소켓
            for i in range(len(chat_room[key_list[index]])):
                user_key = list(user.keys())
                if chat_room[key_list[index]][i][0] == user_key[0]:
                    user_in_room.append(user[chat_room[key_list[index]][i][0]])
        
        msg["rooms"].append({
            "roomId" : roomId,
            "title" : room_title,
            "members" : user_in_room
        })

        index+=1
    send_to_client(sock,msg,sock)

def send_to_client(sock, msg, server_socket):   
    # 사용하지 않는 서버 소켓
    msg_str = None
    # 메세지 제작부분
    serialized = bytes(json.dumps(msg), encoding="utf-8")
    msg_str = json.dumps(msg)

    # TCP 에서 send() 함수는 일부만 전송될 수도 있다.
    # 따라서 보내려는 데이터를 다 못 보낸 경우 재시도 해야된다.
    to_send = len(serialized)
    to_send_big_endian = int.to_bytes(to_send, byteorder="big", length=2)

    # 받는 쪽에서 어디까지 읽어야 되는지 message boundary 를 알 수 있게끔 2byte 길이를 추가한다.
    serialized = to_send_big_endian + serialized

    # print(f"[C->S:총길이={len(serialized)}바이트] 0x{to_send:04x}(메시지크기) {"+ " + msg_str if msg_str else ""}")

    offset = 0
    attempt = 0
    while offset < len(serialized):
        num_sent = sock.send(serialized[offset:])
        if num_sent <= 0:
            raise RuntimeError("Send failed")
        offset += num_sent
        attempt += 1
        print(f"  - send() 시도 #{attempt}: {num_sent}바이트 전송 완료")
    
def is_already_join(sock,is_create):
    key_list = []
    # 현재 존재하는 채팅방의 딕셔너리 key 값 list
    for room in chat_rooms:
        key = list(room.keys())
        key_list.append(key[0])
    index = 0
    # 현재 클라이언트 소켓이 chat_rooms에 있나 검사
    for find_room in chat_rooms:
        if key_list[index] in find_room: # 이거도 아마 문제 있을듯
            for i in find_room[key_list[index]]:
                if sock in i:
                    print("User already has chatRoom")
                    if is_create == False:
                        msg = {
                            "type" : "SCSystemMessage",
                            "text" : "대화 방에 있을 때는 다른 방에 들어갈 수 없습니다."
                        }
                        send_to_client(sock,msg,sock)
                    else:
                        msg = {
                            "type" : "SCSystemMessage",
                            "text" : "대화 방에 있을 때는 방을 개설 할 수 없습니다."
                        }
                        send_to_client(sock,msg,sock)
                    return True
        index+=1
    return False

def consumer_thread():
    # 같은 플래그 써서 종료
    while is_while:     
        with cv:
            print(f"==============={threading.get_native_id()} 쓰레드 대기중====================")
            cv.wait()
            print(f"==============={threading.get_native_id()} 쓰레드 작업 시작====================")

            global queue
                # if not queue:
                #     print("[Queue가 비었습니다]")
                    # cv.wait()
                    # return 0
            print("[producer 스레드 condition notify로 인한 consumer 스레드 시작]")
            job = queue.pop(0)
            command = job[1]["type"]
            if command in command_handlers:
                command_handlers[command](job[0], job[1], job[2])

def main(argv):
    if not FLAGS.port:
        print("서버의 Port 번호를 지정해야 됩니다.")
        # 에러 케이스에 따라 서로 다른 에러코드를 사용할 수도 있다.
        sys.exit(1)
    
    if FLAGS.ip == "127.0.0.1":
        print("서버의 default IP 주소는 127.0.0.1 입니다.")
        # 관례적으로 오류인 경우 0 이 아닌 종료 값을 쓴다.
        # 에러 케이스에 따라 서로 다른 에러코드를 사용할 수도 있다.

    if FLAGS.worker == 2:
        print("서버의 default 워커 스레드 개수는 2개 입니다.")
        print("--worker 옵션으로 워커스레드의 개수 설정 가능합니다. ex) python3 server.py --worker=5")
    print("\n")
    # 서버 정보 설정
    HOST = FLAGS.ip
    PORT = FLAGS.port

    # 서버 소켓 설정
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR 소켓 옵션을 설정
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # 최대 5개의 연결을 대기합니다.

    # 클라이언트 소켓을 기다립니다.
    client_sockets.append(server_socket)

    print(f"서버가 {HOST}:{PORT}에서 실행 중입니다.\n")

    worker_threads = []
    for i in range(FLAGS.worker):
        t2 = threading.Thread(target=consumer_thread)
        t2.daemon = True
        t2.start()
        worker_threads.append(t2)

    while is_while:
        try:
            # select.select()를 사용하여 소켓 상태를 확인합니다.
            readable, _, _ = select.select(client_sockets, [], [], 0.1)
            for sock in readable:
                if sock is server_socket:
                    # 새 클라이언트 연결을 수락합니다.
                    client_socket, client_address = server_socket.accept()
                    client_sockets.append(client_socket)
                    print(f"[새 클라이언트 연결]: {client_address}")
                    users.append({client_socket:client_address})
                else:
                    # 클라이언트로부터 데이터를 받습니다.
                    data = sock.recv(65535)
                    if not data:
                        # 클라이언트 연결 종료
                        print(f"[클라이언트 연결이 끊어졌습니다]: {sock.getpeername()}")
                        client_sockets.remove(sock)
                        sock.close()
                    else:
                        print(f"[클라이언트로부터 받은 메시지]: {data}")
                        # 클라이언트로부터 받은 데이터를 처리합니다.
                        start_index = data.index(b"{")
                        # { 앞은 다 자르고 받음
                        json_data = json.loads(data[start_index:])
                        with cv:
                            queue.append((sock, json_data, server_socket))
                            cv.notify()
        except KeyboardInterrupt:
            break
        except:
            break

command_handlers = {
    "CSCreateRoom": create_chat_room,
    "CSShutdown" : shutdown_server,
    "CSName" : change_user_name,
    "CSChat" : send_to_others,
    "CSJoinRoom" : join_chat_room,
    "CSLeaveRoom" : leave_chat_room,
    "CSRooms" : show_rooms
}

if __name__ == "__main__":
    app.run(main)                    
    