# 2023년 2학기 백엔드소프트웨어개발 Repo
## 개인 정보
- 이름: 유상훈
- 학번: 60172174

# 찾은거 정리

## 윈도우 콘솔 환경에서 ssh 명령어 안될 때

우선 환경변수에

`C:\Users\사용자\Windows\System32\OpenSSH어쩌구`

경로 추가

<br/>

`https://unix.stackexchange.com/questions/464574/ssh-add-returns-with-error-connecting-to-agent-no-such-file-or-directory`

위 링크는 ssh-add가 윈도우 환경에서 안될때,
ssh-agent bash로 initialize해주는거라고 한다.
eval $(ssh-agent)랑 똑같은듯

근데 윈도우는 eval도 안되는거같음

## private key 접근 권한 문제 생길 때

ssh-add로 private key추가하려 할 때, warning과 함께 권한 문제라는 오류가 뜰 수 있다.

윈도우 콘솔환경에서는 또 chmod가 안된다.

`icacls C:\경로\키파일 /inheritance:r /grant:r "사용자 이름:R"`를 하면 권한 변경된다.

이 때, icacls 명령어를 실행할 때, icacls를 또 환경변수에 추가하거나 System32 디렉토리 내에서 실행하면 된다.
