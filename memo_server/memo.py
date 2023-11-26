from http import HTTPStatus
import random
import requests
import json
import urllib
import psycopg2, psycopg2.extras

from flask import abort, Flask, make_response, render_template, redirect, request
# from credentials import DATABASE as DB

app = Flask(__name__)

# 본인의 로컬 환경에서는 python3 -m flask --app memo run --port 8080 명령어로 실행

naver_client_id = 'Py8QuVo4SDJNdVdeVTEZ'
naver_client_secret = 'zmQgnNNDt9'
naver_redirect_uri = 'http://localhost:8080/auth'
naver_redirect_uri_auth = 'http://localhost:8080/'
'''
  본인 app 의 것으로 교체할 것.
  여기 지정된 url 이 http://localhost:8000/auth 처럼 /auth 인 경우
  아래 onOAuthAuthorizationCodeRedirected() 에 @app.route('/auth') 태깅한 것처럼 해야 함
'''
def connect_db():
    conn = psycopg2.connect(
        host="postgres-container", # docker 이용해서 DB 접근할때는, DB 이름으로 원래는 127.0.0.1
        dbname="postgres",
        user="postgres",
        password="y3558325",
        port=5432,
    )
    conn.autocommit = True
    return conn

@app.route('/')
def home():
    # 쿠기를 통해 이전에 로그인 한 적이 있는지를 확인한다.
    # 이 부분이 동작하기 위해서는 OAuth 에서 access token 을 얻어낸 뒤
    # user profile REST api 를 통해 유저 정보를 얻어낸 뒤 'userId' 라는 cookie 를 지정해야 된다.
    # (참고: 아래 onOAuthAuthorizationCodeRedirected() 마지막 부분 response.set_cookie('userId', user_id) 참고)
    userId = request.cookies.get('userId', default=None)
    name = None

    ####################################################
    # TODO: 아래 부분을 채워 넣으시오.
    # userId 로부터 DB 에서 사용자 이름을 얻어오는 코드를 여기에 작성해야 함
    if userId:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(f"SELECT name from users WHERE id = '{userId}';")
        name = cur.fetchone()[0]
        
        cur.close()
        conn.close()
    ####################################################

    # 이제 클라에게 전송해 줄 index.html 을 생성한다.
    # template 로부터 받아와서 name 변수 값만 교체해준다.
    return render_template('index.html', name=name)


# 로그인 버튼을 누른 경우 이 API 를 호출한다.
# OAuth flow 상 브라우저에서 해당 URL 을 바로 호출할 수도 있으나,
# 브라우저가 CORS (Cross-origin Resource Sharing) 제약 때문에 HTML 을 받아온 서버가 아닌 곳에
# HTTP request 를 보낼 수 없는 경우가 있다. (예: 크롬 브라우저)
# 이를 우회하기 위해서 브라우저가 호출할 URL 을 HTML 에 하드코딩하지 않고,
# 아래처럼 서버가 주는 URL 로 redirect 하는 것으로 처리한다.
# 주의! 아래 API 는 잘 동작하기 때문에 손대지 말 것
@app.route('/login')
def onLogin():
    params={
            'response_type': 'code',
            'client_id': naver_client_id,
            'redirect_uri': naver_redirect_uri,
            'state': random.randint(0, 10000)
        }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/authorize?{urlencoded}'
    return redirect(url)

# 아래는 Redirect URI 로 등록된 경우 호출된다.
# 만일 본인의 Redirect URI 가 http://localhost:8000/auth 의 경우처럼 /auth 대신 다른 것을
# 사용한다면 아래 @app.route('/auth') 의 내용을 그 URL 로 바꿀 것
@app.route('/auth')
def onOAuthAuthorizationCodeRedirected():
    # TODO: 아래 1 ~ 4 를 채워 넣으시오.
    # 1. redirect uri 를 호출한 request 로부터 authorization code 와 state 정보를 얻어낸다.
    code = request.args.get('code')
    state = request.args.get('state')

    # 2. authorization code 로부터 access token 을 얻어내는 네이버 API 를 호출한다.
    params={
            'grant_type': 'authorization_code',
            'client_id': naver_client_id,
            'client_secret': naver_client_secret,
            'code' : code,
            'state': state
    }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/token?{urlencoded}'
    response = requests.post(url)
    access_token = response.json()["access_token"]

    # 3. 얻어낸 access token 을 이용해서 프로필 정보를 반환하는 API 를 호출하고,
    #    유저의 고유 식별 번호를 얻어낸다.
    header = "Bearer " + access_token # Bearer 다음에 공백 추가
    url = "https://openapi.naver.com/v1/nid/me"
    request_url = urllib.request.Request(url)
    request_url.add_header("Authorization", header)
    response = urllib.request.urlopen(request_url)
    rescode = response.getcode()

    user_id = None
    user_name = None
    if(rescode==200):
        response_body = response.read()
        json_string = response_body.decode('utf-8')
        data = json.loads(json_string)
        user_id = data['response']['id']
        user_name = data['response']['name']
    else:
        print("Error Code:" + rescode)

    # 4. 얻어낸 user id 와 name 을 DB 에 저장한다.
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE tablename = 'users');")
        exists = cur.fetchone()[0]

        if exists == True:
            print("users 테이블이 이미 존재하므로 테이블을 생성하지 않습니다.")
            cur.execute("INSERT INTO users (id, name) VALUES (%s, %s);", (user_id, user_name))
            cur.execute("SELECT * FROM users;")
            print(f"유저 db생성 완료, 현재 users 테이블 목록 \n{cur.fetchall()}\n")
        else:
            cur.execute("CREATE TABLE users(id text PRIMARY KEY, name text);")
            cur.execute("INSERT INTO users (id, name) VALUES (%s, %s);", (user_id, user_name))
            cur.execute("SELECT * FROM users;")
            print(f"유저 db생성 완료, 현재 users 테이블 목록 \n{cur.fetchall()}\n")
        conn.commit()
        # 5. 첫 페이지로 redirect 하는데 로그인 쿠키를 설정하고 보내준다.
        response = redirect('/')
        response.set_cookie('userId', user_id)
    except psycopg2.IntegrityError as e:
        # print(f"에러발생: ",type(e))
        print("이미 존재하는 회원이므로, 로그인 처리")
        response = redirect('/')
        response.set_cookie('userId', user_id)
    except psycopg2.DatabaseError as e:
        print("error: ", type(e))
        print("알 수 없는 데이터베이스 에러")
        conn.rollback()
        response = redirect('/')
    finally:
        cur.close()
        conn.close()
    return response


@app.route('/memo', methods=['GET'])
def get_memos():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # TODO: DB 에서 해당 userId 의 메모들을 읽어오도록 아래를 수정한다.
    result = []
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM memos WHERE user_id = '{userId}';")
    cur_fetch = cur.fetchall()
    for i in cur_fetch:
        memos = {
            'userId' : i[2], # memos 테이블의 세 번째 컬럼 값 -> user_id
            'text' : i[1] # memos 테이블의 두 번째 컬럼 값 -> text
        }
        result.append(memos)
    cur.close()
    conn.close()
    # memos라는 키 값으로 메모 목록 보내주기
    return {'memos': result}


@app.route('/memo', methods=['POST'])
def post_new_memo():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # 클라이언트로부터 JSON 을 받았어야 한다.
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)

    # TODO: 클라이언트로부터 받은 JSON 에서 메모 내용을 추출한 후 DB에 userId 의 메모로 추가한다.
    conn = connect_db()
    cur = conn.cursor()
    text = request.json['text']

    cur.execute(f"INSERT INTO memos (text, user_id) VALUES('{text}','{userId}');")
    cur.close()
    conn.close()
    #
    return '', HTTPStatus.OK

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)