# from socket import *
# import json
# import select
# import threading

# host = "127.0.0.1"
# port = 9123

# # 쓰레드를 추적할 리스트 생성
# active_threads = []
# server_running = True  # 서버 동작 여부를 추적하는 플래그

# def handle_client(client_socket):
#     # server_running 플래그에 뮤텍스를 설정
#     lock = threading.Lock()
#     while True:
#         with lock:
#             running = server_running
#         data = client_socket.recv(1024)
#         if not data:
#             break
#         start_index = data.index(b'{')
#         json_data = json.loads(data[start_index:])
#         print(f'받은 데이터 type: {json_data["type"]}')
#         if json_data["type"] == "CSShutdown":
#             print("shutdown 입력받음, 종료")
#             # 모든 클라이언트의 연결을 끊음
#             for thread in active_threads:
#                 thread.join()
#             # server_running 플래그의 값을 변경
#             with lock:
#                 running = False
#             break  # 스레드를 종료하고 서버를 종료
#         else:
#             client_socket.send("I am server".encode("utf-8"))
#             print("메시지를 보냈습니다")
#     client_socket.close()


# def main():
#     serverSocket = socket(AF_INET, SOCK_STREAM)
#     serverSocket.bind((host, port))
#     serverSocket.listen(5)

#     print("서버 대기 중입니다.")

#     while server_running:
#         client_socket, addr = serverSocket.accept()
#         print(f'{str(addr)}에서 접속되었습니다')
#         client_thread = threading.Thread(target=handle_client, args=(client_socket,))
#         client_thread.start()
#         # 쓰레드를 active_threads 리스트에 추가
#         active_threads.append(client_thread)
    
# if __name__ == "__main__":
#     main()

import socket
import select
import json
import codecs

# 서버 정보 설정
HOST = "127.0.0.1"
PORT = 9123

# 클라이언트 소켓을 관리하기 위한 리스트
client_sockets = []

# 서버 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        else:
            # 클라이언트로부터 데이터를 받습니다.
            data = sock.recv(1024)
            if not data:
                # 클라이언트 연결 종료
                print(f"클라이언트 연결이 끊어졌습니다: {sock.getpeername()}")
                client_sockets.remove(sock)
                sock.close()
            else:
                print(f"클라이언트로부터 받은 메시지: {data}")

                # 클라이언트로부터 받은 데이터를 처리합니다.
                start_index = data.index(b'{')
                # { 앞은 다 자르고 받음
                json_data = json.loads(data[start_index:])
                print(f'받은 데이터 type: {json_data["type"]}')

                if json_data["type"] == "CSShutdown":
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
                