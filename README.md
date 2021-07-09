# Django API Server

## Python Version
* 3.9.5

## 패키지 설치
* 개발
```shell
# 프로젝트의 root 경로에서 아래 명령을 실행합니다.

pip install -r ./requirements/dev.txt
```
* 운영
```shell
# 프로젝트의 root 경로에서 아래 명령을 실행합니다.

pip install -r ./requirements/prod.txt
```

## .env

```dotenv
# Database Example
DATABASE_URL=mysql://user:%23password@127.0.0.1:3306/dbname
```

## 서버 구동
```shell
# 프로젝트의 root 경로에서 아래 명령을 실행합니다.

# runserver 구동
sh run.sh
```