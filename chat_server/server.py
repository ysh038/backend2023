import socket
import select
import json
import sys
from absl import app, flags

# 서버 정보 설정
HOST = "127.0.0.1"
PORT = 9123
# 일단 FLAG 사용 X
# FLAGS = flags.FLAGS

# flags.DEFINE_string(name='ip', default='127.0.0.1', help='서버 IP 주소')
# flags.DEFINE_integer(name='port', default=None, required=True, help='서버 port 번호')
# flags.DEFINE_enum(name='format', default='json', enum_values=['json', 'protobuf'], help='메시지 포맷')

# 클라이언트 소켓을 관리하기 위한 리스트
client_sockets = []

# 채팅방을 저장할 리스트
chat_rooms = []

# 유저 소켓정보와 이름을 저장할 딕셔너리 리스트
users = []

# roomId 배정 정수형 변수
room_count = 1

# 채팅방이름과 소켓을 Key
def create_chat_room(sock,title):
    global room_count
    chat_room_group = []
    chat_room = []
    # chat_room 의 인덱스0 = 소켓, 인덱스1 = title
    chat_room.append(sock)
    chat_room.append(title)
    chat_room_group.append(chat_room)
    chat_rooms.append({room_count:chat_room_group})
    print(f"Create Chat Room, roomId is {room_count}")
    print("chatRooms: ",chat_rooms)

    room_count += 1

    # if FLAGS.format == 'json':
    msg = {
        'type' : 'SCSystemMessage',
        'text' : '[' + title + '] 방에 입장했습니다.'
    }
    send_to_client(sock,msg)

    # chat_rooms에서 특정 sock 찾기 (이후 채팅방 나가기, 삭제 위해 미리 구현)
    # socket_to_delete = sock
    # socket_index = 0
    # for find_room in chat_rooms:
    #     if sock in find_room:
    #         socket_index = chat_rooms.index(find_room)
    #         del find_room[socket_to_delete]
    #         del chat_rooms[socket_index]

def join_chat_room(sock, roomId):
    index = 1
    for find_room in chat_rooms:
        for i in find_room[index]:
            if sock in i:
                print(True,i[1])
                msg = {
                    'type' : 'SCSystemMessage',
                    'text' : '이미 채팅방에 들어가있습니다.'
                }
                send_to_client(sock,msg)
                return 0
        index+=1
    global room_count
    chat_room = []
    for room in chat_rooms:
        if roomId in room:
            chat_room.append(sock)
            # title
            chat_room.append(room[roomId][0][1])
            room[roomId].append(chat_room)


def change_user_name(sock, new_name):
    # print("인자 소켓: ",sock.getsockname())
    for user in users:
        if sock in user:
            user[sock] = new_name

    # if FLAGS.format == 'json':
    msg = {
        'type' : 'SCSystemMessage',
        'text' : '유저 이름이 ' + new_name + ' 으로 변경되었습니다.'
    }
    send_to_client(sock,msg)

def send_to_others(sock, json_data):
    for user in users:
        if sock in user:
            send_user_name = user[sock]
            print("send_user_name : " , send_user_name)

    msg = {
        'type' : 'SCChat',
        'member' : send_user_name,
        'text' : json_data['text']
    }

    for user in users:
        if sock in user:
            print("",end="")
        else:
            for key in user.keys():
                send_to_client(key,msg)
            # send_to_client(sockets[0],msg)

def shutdown_server(server_socket):
    # 모든 클라이언트의 연결을 끊음
    # 여기에 데이터 처리 로직을 추가합니다.
    # 모든 클라이언트 연결을 종료하는 조건
    print("서버와 모든 클라이언트 연결을 종료합니다.")

    for client_sock in client_sockets:
        if client_sock is not server_socket:
            client_sock.send("서버가 종료됩니다.".encode('utf-8'))
            client_sock.close()
    server_socket.close()
    exit()

def send_to_client(sock, msg):
    # 메세지 제작부분
    msg_str = None
    serialized = bytes(json.dumps(msg), encoding='utf-8')
    msg_str = json.dumps(msg)

    # TCP 에서 send() 함수는 일부만 전송될 수도 있다.
    # 따라서 보내려는 데이터를 다 못 보낸 경우 재시도 해야된다.
    to_send = len(serialized)
    to_send_big_endian = int.to_bytes(to_send, byteorder='big', length=2)

    # 받는 쪽에서 어디까지 읽어야 되는지 message boundary 를 알 수 있게끔 2byte 길이를 추가한다.
    serialized = to_send_big_endian + serialized

    # print(f'[C->S:총길이={len(serialized)}바이트] 0x{to_send:04x}(메시지크기) {"+ " + msg_str if msg_str else ""}')

    offset = 0
    attempt = 0
    while offset < len(serialized):
        num_sent = sock.send(serialized[offset:])
        if num_sent <= 0:
            raise RuntimeError('Send failed')
        offset += num_sent
        attempt += 1
        # print(f'  - send() 시도 #{attempt}: {num_sent}바이트 전송 완료')
# 메세지 제작부분

def main():
    # FLAG는 아직 사용하지 않음
    # if not FLAGS.ip:
    #     print('서버의 IP 주소를 지정해야 됩니다.')
    #     # 관례적으로 오류인 경우 0 이 아닌 종료 값을 쓴다.
    #     # 에러 케이스에 따라 서로 다른 에러코드를 사용할 수도 있다.
    #     sys.exit(1)

    # if not FLAGS.port:
    #     print('서버의 Port 번호를 지정해야 됩니다.')
    #     # 에러 케이스에 따라 서로 다른 에러코드를 사용할 수도 있다.
    #     sys.exit(2)

    # 서버 소켓 설정
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR 소켓 옵션을 설정
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # 최대 5개의 연결을 대기합니다.

    # 클라이언트 소켓을 기다립니다.
    client_sockets.append(server_socket)

    print(f"서버가 {HOST}:{PORT}에서 실행 중입니다.")

    while True:
        # select.select()를 사용하여 소켓 상태를 확인합니다.
        readable, _, _ = select.select(client_sockets, [], [])

        for sock in readable:
            if sock is server_socket:
                # 새 클라이언트 연결을 수락합니다.
                client_socket, client_address = server_socket.accept()
                client_sockets.append(client_socket)
                print(f"새 클라이언트 연결: {client_address}")
                users.append({client_socket:client_address})
            else:
                # 클라이언트로부터 데이터를 받습니다.
                data = sock.recv(65535)
                if not data:
                    # 클라이언트 연결 종료
                    print(f"클라이언트 연결이 끊어졌습니다: {sock.getpeername()}")
                    client_sockets.remove(sock)
                    sock.close()
                else:
                    # print(f"클라이언트로부터 받은 메시지: {data}")

                    # 클라이언트로부터 받은 데이터를 처리합니다.
                    start_index = data.index(b'{')
                    # { 앞은 다 자르고 받음
                    json_data = json.loads(data[start_index:])
                    message_type = json_data["type"]
                    # print(f'받은 데이터 type: {json_data["type"]}')

                    if message_type == "CSCreateRoom":
                        new_room_title = json_data["title"]
                        create_chat_room(sock,new_room_title)
                    elif message_type == "CSShutdown":
                        shutdown_server(server_socket)
                    elif message_type == "CSName":
                        new_user_name = json_data["name"]
                        change_user_name(sock,new_user_name)
                    elif message_type == "CSChat":
                        send_to_others(sock,json_data)
                    elif message_type == "CSJoinRoom":
                        roomId = json_data["roomId"]
                        join_chat_room(sock,roomId)


message_type_handlers = {
    'CSCreateRoom': create_chat_room
}

if __name__ == "__main__":
    main()                    