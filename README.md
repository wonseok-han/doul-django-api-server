# Django API Server

## Python Version
* 3.9.5

## Database
* MySql

## Package Install
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

## Migration
```shell
#  Migrate 상태 Show
python manage.py showmigrations

# Migration 파일 생성
python manage.py makemigrations "앱명"

# 생성된 Migration 파일에 대한 SQL 스크립트 출력
python manage.py sqlmigrate "앱명" "마이그레이션 파일 번호"

# Migration 파일을 토대로 Migrate
python manage.py migrate_refactored "앱명"

# MultiDB로 연결된 DB Migrate시 아래 명령 사용
python manage.py migrate_refactored --database "Alias DB명"
```

## Run Server
```shell
# 프로젝트의 root 경로에서 아래 명령을 실행합니다.

# runserver 구동
sh run.sh
```