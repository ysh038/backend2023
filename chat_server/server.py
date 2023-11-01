from socket import *
import json

host = "127.0.0.1"
port = 9123

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host,port))
serverSocket.listen(1)

connectionSocket,addr = serverSocket.accept()
print(str(addr),"에서 접속되었습니다")
print("서버 대기중입니다.")

while(1):
    data = connectionSocket.recv(1024)
    print(f'  - recv(): {len(data)}바이트 읽음')

    start_index = data.index(b'{')

    # 시작 위치부터 끝까지의 부분을 추출하여 JSON 문자열로 처리
    json_data = json.loads(data[start_index:])

    print("받은 데이터 type:",json_data["type"])

    if json_data["type"] == "CSShutdown":
        print("shutdown 입력받음, 종료")
        break
    else:  
        connectionSocket.send("I am server".encode("utf-8"))
        print("메시지를 보냈습니다.")

serverSocket.close()

# if __name__ == "__main__":
#     main()