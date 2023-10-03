# 2023년 2학기 백엔드소프트웨어개발 Repo
## 개인 정보
- 이름: 유상훈
- 학번: 60172174

<br/>
<br/>
<br/>
<br/>
<br/>


# 수업 내용 외 찾은거 정리

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

## Python main함수 실행에 관해
파이썬으로 main함수가 존재하는 코드를 처음 짜봐서 생긴 이슈

python3 명령어를 통해 코드를 실행했더니, 아무것도 출력되지가 않았음

혹시나해서 알아봤더니 아래 코드를 쓰지 않으면 main함수가 실행되지 않는것이었다.

```python
if __name__ == '__main__':
    main(sys.argv)
```

gpt에게 물어봤다.

```
if __name__ == '__main__':
    main(sys.argv)
이건 파이썬에서 관례젹으로 쓰이는 표현이야?
```

```
네, if __name__ == '__main__':은 파이썬 코드에서 자주 사용되는 관례적인 표현입니다. 이 표현은 스크립트가 직접 실행될 때 코드 블록을 실행하도록 하는데 사용됩니다.

파이썬 스크립트를 실행할 때, 스크립트 파일이 최상위 레벨에서 직접 실행되는 경우 __name__ 변수는 '__main__'으로 설정됩니다. 이것은 스크립트가 다른 모듈에서 임포트되었을 때와 구별하기 위한 것입니다. 다시 말해, 스크립트가 다른 스크립트나 모듈에서 임포트되는 경우 __name__은 해당 모듈의 이름이 됩니다.

따라서 if __name__ == '__main__':을 사용하면 스크립트 파일이 직접 실행될 때만 특정 코드 블록이 실행되고, 다른 스크립트나 모듈에서 임포트될 때는 실행되지 않습니다. 이것은 주로 스크립트 파일을 모듈로 사용할 때 유용합니다.
``