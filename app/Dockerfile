# Dockerfile
# Use the official Python image from the Docker Hub
# 검색: https://hub.docker.com/_/python
# python:alpine: Alpine build linux로, 가장 가볍고 용량이 적으며 bash도 없음, apk 사용. sh로 shell 접근
# python:slim: debian 기반 linux로, 그 중에서도 가벼운 편
# python:bullseye: debian 11
# python:bookwarm: debian 12
# 용량이 매우 중요한 것이 아니라면 slim 버전에 필요한 모듈을 추가하는 것을 추천함.

FROM python:3.12-slim
WORKDIR /app/
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ADD . ./

# CMD는 최대 1개까지 실행할 수 있음
# CMD ["sleep", "86400"]
CMD ["python", "main.py"]
