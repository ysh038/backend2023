# 메모장 서비스 만들기

### 구성
- static 폴더
    - 네이버 로그인 버튼 이미지
- templates 폴더
    - index.html
- memo.py
- readme.md
- requirements.txt

### 실행 방법

1. aws instance에 접속 후 파일 업로드

2. requirement에 명시된 패키지 설치
    > pip install -r requirement.txt 

3. nginx + uWSGI가 자동으로 static 파일들과 mjubackend/memo.py를 로드

4. 네이버 API callback uri 설정

### 코드 설명

#### 전역변수 

네이버 API 사용을 위한 변수
>**naver_client_id , naver_client_secret**

네이버 로그인 API가 response를 callback할 uri 
>**naver_redirect_uri**

#### 함수

>**connect_db**

Mysql DB에 연결하고 connection 객체 반환

>**home**

cookie를 통해 로그인이 되어있는지 확인 후, index.html 반환하는 함수

>**login**

네이버 oauth2 로그인 API에 코드를 요청하는 함수, code를 파라미터에 넣어 /auth 로 redirect 한다.

>**onOAuthAuthorizationCodeRedirected**

code를 통해 accessToken을 네이버 API에 요청한다.
얻어낸 토큰을 통해 네이버 계정 정보 (고유 ID, 이름)를 가져와 Mysql 테이블을 생성하고, 유저 정보를 DB에 저장한다.

>**get_memos**

현재 로그인 되어있는 유저의 메모 리스트를 DB로부터 가져온다. 메모 리스트를 반환한다.

>**post_new_memo**

클라이언트가 입력한 메모를 JSON형태로 입력받고 Mysql DB에 저장한다.

### AWS ELB를 통해 실제 배포된 환경
>http://60172174-lb-1059453829.ap-northeast-2.elb.amazonaws.com/memo
