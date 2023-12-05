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

### 그 외 사항

uwsgi Restart해야 바뀐 파일 적용

>sudo systemctl restart uwsgi-app@memo.service 
>sudo service nginx restart

nginx log 추적

>tail -f /var/log/nginx/error.log </br>
tail -f /var/log/nginx/access.log

##### postgresql 이미지 설치

ec2 에서 할땐, sudo 붙여야함

>docker pull postgres

>docker docker run 
-dp 5432:5432 
--name postgresql 
-e POSTGRES_PASSWORD=1234 
-v 호스트 패키지 경로:/var/lib/postgres/data postgres

##### docker shell 접속

>sudo docker exec -it postgres /bin/bash

##### postgresql 접속

>psql -U postgres

##### login 앞에는 /memo prefix 하면 안되는 이유

 ~~index.html에서 login 버튼의 onClick 이벤트를 보니까, window.location 으로 되어있어서 앱 내부에서 redirect 하는 식으로 해서 앞에 prefix 빼도 되는듯~~

~~prefix를 하는건 브라우저에서 직접 request할때만? 아마도?~~

##### mysql docker 컨테이너 접속하기

>$sudo docker exec -it mysql-container bash

>$mysql -uroot -p

##### mysql 컬럼 utf8 오류 뜰때
>"ALTER TABLE mytable MODIFY name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_bin;"

##### mysql flask에서 execute해도 적용 안될 때
cur.commit 같은것을 해야함!!

##### wsgi 서버에 띄워진 앱 로깅하기
``` python
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/path/to/your/log/file.log',
            'formatter': 'default',
            'maxBytes': 1024 * 1024,
            'backupCount': 10
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
```
> 출처: https://flask.palletsprojects.com/en/2.3.x/logging/