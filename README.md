# 게시판 REST API

FastAPI, PostgreSQL, SQLAlchemy로 만든 게시판 API입니다. Swagger UI에서 회원가입·로그인과 게시글 CRUD를 실행할 수 있습니다. 게시글은 공개 조회가 가능하며, 로그인한 회원만 작성할 수 있습니다. 작성자와 관리자는 게시글을 수정·삭제할 수 있습니다.

## 프로젝트 구조

회원과 게시글을 기능별로 묶고 각 기능 내부를 4계층으로 구성했습니다.

```text
app/
├─ users/
│  ├─ application/service.py
│  ├─ domain/
│  │  ├─ user.py
│  │  └─ repository.py
│  ├─ infrastructure/
│  │  ├─ models.py
│  │  └─ repositories.py
│  └─ presentation/
│     ├─ router.py
│     ├─ dependencies.py
│     └─ schemas.py
├─ posts/
│  ├─ application/service.py
│  ├─ domain/
│  │  ├─ post.py
│  │  └─ repository.py
│  ├─ infrastructure/
│  │  ├─ models.py
│  │  └─ repositories.py
│  └─ presentation/
│     ├─ router.py
│     ├─ dependencies.py
│     └─ schemas.py
├─ config.py
├─ db.py
├─ security.py
└─ main.py
```

- application은 회원가입·로그인과 게시글 처리 흐름을 담당합니다.
- domain은 회원·게시글 데이터와 저장소 인터페이스를 정의합니다.
- infrastructure는 SQLAlchemy 모델과 저장소 구현을 담당합니다.
- presentation은 라우터, 요청·응답 스키마와 의존성을 연결합니다.

## 로컬 실행

1. PostgreSQL과 uv를 설치합니다. PostgreSQL 관리자 계정으로 아래 SQL을 실행합니다. 비밀번호는 사용할 값으로 바꿉니다.

   ```sql
   CREATE USER board WITH PASSWORD 'your-password';
   CREATE DATABASE board OWNER board;
   ```

2. `.env.example`을 `.env`로 복사합니다. 기존 `.env`가 있다면 연결 정보를 수정합니다. `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`를 실제 PostgreSQL 설정에 맞추고, `JWT_SECRET`에는 최소 32자의 임의 문자열을 입력합니다.

   ```powershell
   uv sync --locked
   uv run python -c "import secrets; print(secrets.token_hex(32))"
   uv run uvicorn app.main:app --reload
   ```

3. [Swagger UI](http://localhost:8000/docs)를 엽니다. 서버 시작 시 필요한 테이블이 자동 생성됩니다. [상태 확인](http://localhost:8000/health)에서 DB 연결을 확인할 수 있습니다.

## API

| 메서드 | 경로 | 동작 |
|---|---|---|
| POST | `/auth/signup` | 사용자명과 비밀번호로 가입 |
| POST | `/auth/login` | 폼 데이터로 로그인하고 JWT 발급 |
| GET | `/auth/me` | 현재 로그인 사용자 확인 |
| GET | `/posts` | 목록 조회. `offset`, `limit` 지원 |
| GET | `/posts/{post_id}` | 게시글 상세 조회 |
| POST | `/posts` | 게시글 작성 |
| PUT | `/posts/{post_id}` | 작성자 또는 관리자가 수정 |
| DELETE | `/posts/{post_id}` | 작성자 또는 관리자가 삭제 |

Swagger UI에서 **POST /auth/signup**을 실행한 뒤 상단 **Authorize**에 같은 사용자명과 비밀번호를 입력합니다. 로그인 이후 제목과 내용으로 게시글을 생성합니다. 다른 회원으로 로그인해 같은 게시글을 수정하면 `403`이 반환됩니다.

비밀번호는 Argon2 해시로 저장합니다. JWT의 기본 만료 시간은 30분이며 `TOKEN_MINUTES`로 설정합니다. 회원가입 시 역할은 `member`로 지정됩니다. 관리자 역할이 필요하면 DB 운영자가 해당 계정의 `users.role`을 `admin`으로 변경합니다. 외부 웹 프런트엔드에서 호출할 경우 `CORS_ORIGINS`에 허용할 사이트를 JSON 배열로 설정할 수 있습니다.

## PostgreSQL 연동 테스트

별도 PostgreSQL 테스트 DB를 만든 뒤 연결 환경 변수를 설정합니다. 예를 들어 `POSTGRES_DB=board_test`를 설정하고 아래 명령을 실행합니다.

```bash
uv run python -m unittest discover -s tests -v
```

테스트 DB에는 테스트 계정이 생성됩니다. 테스트는 Swagger 문서, 회원가입과 로그인, 토큰 만료, 게시글 CRUD와 작성자·관리자 권한을 확인합니다.

## AWS EC2 배포

1. EC2에 Python, uv와 PostgreSQL을 준비하고 이 저장소를 클론합니다.
2. 로컬 실행과 같은 방식으로 DB 계정과 데이터베이스, `.env`를 준비합니다.
3. `uv sync --locked --no-dev`로 설치한 뒤 `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`으로 접속을 확인합니다.
4. EC2 보안 그룹의 TCP 8000을 열었다면 `http://퍼블릭IP:8000/docs`에서 Swagger에 접근할 수 있습니다. SSH는 접속할 IP에 허용합니다.
5. 계속 실행할 때는 systemd에 Uvicorn 실행 명령과 프로젝트 작업 디렉터리를 등록합니다. 도메인과 HTTPS를 사용하는 경우 리버스 프록시를 통해 `127.0.0.1:8000`으로 연결합니다.

과제에는 GitHub URL과 실제 접속 가능한 API·Swagger UI 주소를 제출합니다.
