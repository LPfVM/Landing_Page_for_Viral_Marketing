FROM python:3.13

# 컨테이너 안에서 작업 디렉토리를 /app으로 설정
WORKDIR /app

RUN pip install uv

# toml과 lock을 현재위치(app) 안으로 복사
COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

# 현재 위치(프로젝트 루트)의 모든 파일과 디렉토리를 컨테이너의 현재 위치(app)에 복사
COPY . .

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
