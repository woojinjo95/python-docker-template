
## 명령어 설명

### Docker Compose로 컨테이너에 접속하기
```
docker-compose exec -it app bash
```
docker-compose exec: 실행 중인 서비스 컨테이너에 명령을 실행합니다.
-it: 인터랙티브 모드로 터미널을 엽니다.
app: docker-compose.yml 파일에 정의된 서비스 이름입니다.
bash: 컨테이너 내에서 bash 셸을 실행합니다.

### Docker Compose로 컨테이너 빌드 및 백그라운드 실행
```
docker-compose up -d --build
```
docker-compose up: Docker Compose로 정의된 서비스를 시작합니다.
-d: 백그라운드 모드로 컨테이너를 실행합니다.
--build: 컨테이너를 시작하기 전에 이미지를 다시 빌드합니다.

### Docker Compose 로그 실시간 보기
```
docker-compose logs -f app
```

## 파일 설명

### Root
* docker-compose.yml
여러 컨테이너에 대해 정의된 yml 파일로, 한 번에 컨테이너를 실행하고 내부 변수를 관리할 수 있습니다.
* .env
환경 변수 정의 파일입니다.
* README.md
이 파일입니다.
### app
* Dockerfile
python을 실행할 컨테이너의 구성 파일입니다. 기본은 main.py를 실행하는 것이나, 단순히 sleep를 실행하는 옵션을 사용할 수도 있습니다.
* requirements.txt
python에서 사용할 라이브러리를 저장하는 파일입니다. 도커 빌드 시 먼저 라이브러리 설치가 실행됩니다. 
* main.py
실행될 python 파일의 기본 정의입니다. 이름 변경 시 Dockerfile 실행도 변경해야 합니다. 
* log_organizer.py
멀티프로세스를 이용하더라도 하나의 로그 파일로 저장할 수 있도록 정의하고, 필요에 따라 강조 표시가 가능하도록하는 라이브러리입니다. 멀티프로세스로 실행되기 때문에 main.py에서 무조건 종료될 수 있도록 구성되어 있습니다. 모든 로그는 ./logs 폴더 아래 저장되며, 하루에 한 번씩 분리되어 아카이빙됩니다.