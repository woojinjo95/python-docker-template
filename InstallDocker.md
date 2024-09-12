# WSL
## 기본 설정 
- Windows 기능 켜기/끄기에서 다음 2개를 활성화: Hyper-V, Linux용 Windows 하위 시스템
- 재부팅 필요

## 스토어 이용 가능
커맨드/파워쉘을 이용해 한 번에 설치
```
wsl --install -d Ubuntu
```

## 스토어 이용 불가
위와 같은 명령어 입력 시, 다음 오류가 발생함
```
> wsl --install -d Ubuntu
설치 중 오류가 발생했습니다. 배포 이름: 'Ubuntu' 오류 코드: 0x8000ffff
```

먼저 linux 시스템 설치, 배포패키지 제외
```
wsl --install
```

마이크로소프트 스토어 이용이 불가하면 아래와 같이 파워쉘에서 appx 파일로 다운로드 (~1.2 GB)
```
Invoke-WebRequest -Uri https://aka.ms/wslubuntu2204 -OutFile Ubuntu.appx -UseBasicParsing
```

이후 아래 명령어로 설치 진행하는 게 정상적인 방법임. 그러나 볼륨이 잡히지 않기 때문에, 실행 X
```
# Add-AppxPackage .\Ubuntu.appx 
```
- Ubuntu.appx 파일을 압축해제하여 안에 있는 것 중 아키텍쳐에 맞는 것을 다시 압축 해제, 일반적으로 Ubuntu_2204.1.7.0_x64.appx
- 안에 있는 ubuntu.exe를 실행하면 설치가 됨, 그러나 vhd 파일이 해당 경로에 생성되며, 기본 20GB 는 차지하므로 용량 주의
- 만약 여러개 버전의 리눅스를 설치했고 하나만 사용할 것이라면, 이전 리눅스는 `wsl --list` 명령을 이용해 확인후 `wsl --unregister <distro>` 로 삭제하거나 우선순위 

## 주의사항
- 만약 wsl2가 아니라 wsl1이 설치되면 여러 기능을 사용할 수 없음. 특히 nvidia gpu 연동 등 치명적인 기능들
- 웬만하면 wsl2가 자동으로 설치되나, `wsl --list --verbose` 시 버전이 1이고 `wsl --set-default-version 2` 나 `wsl --set-version <distro> 2` 도 안 막히면 wsl2로 새로 설치

## wsl 재설치법
- 먼저 앱 및 기능에서 linux 배포판, 일반적으로 Ubuntu를 삭제
- 이후 `wsl --unregister <distro>` 를 입력해 등록 해제
- 윈도우 기능/켜기 옵션에서 wsl 기능 해제 후 재부팅
- 윈도우 기능/켜기 옵션에서 wsl 기능 선택 후 다시 재부팅
- 설치 진행

# Docker
## 임의의 Ubuntu에 Docker 설치
```
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce
sudo service docker start
```
- 필수 패키지 설치 후 gpg key (GNU Public Guard key) 키 추가
- 현재 우분투 배포판에 맞는 Docker 저장소 추가
- apt update로 추가한 저장소 목록 업데이트
- docker community edition을 설치
- docker 서비스 시작

## Docker 실행 권한을 user에게 할당
```
sudo usermod -aG docker $USER
cat /etc/group | grep docker
```
- 현재 접속한 아용자에 대해 권한 추가, sudo 없이 docker 관련 작업 가능
- docker 그룹 추가 확인
- shell 재실행 시 적용됨

## Docker 상태 확인
```
docker -v
docker ps
```
- 만약 ubuntu 22.04 버전 이상에서 service 시작을 해도 켜지지 않는다면, `sudo dockerd` 로 에러 원인 확인 후 진행
- 해당 에러가 네트워크 NAT 등에 대한 에러라면, iptables 관련 에러이므로 다음을 실행 후 다시 확인
```
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
```
- 이렇게 한 뒤에 dockerd 로는 실행되는데 service로는 안 올라온다면
```
sudo update-alternatives --config iptables
```
입력 후 1을 선택해 iptables-legacy를 선택


# Docker-compose
## docker-compose 설치
아래 작업은 일정 버전 이상의 docker에서는 `docker compose`가 `docker-compose`를 대체하므로 굳이 필요하지 않음.

```
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

- 현재 linux에 맞는 docker-compose 설치
- chmod로 파일 실행 권한 부여
- symbolic link를 생성하여 모든 경로에서 docker-compose 실행할 수 있도록 함
