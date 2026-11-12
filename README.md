# 게시판 REST API

FastAPI, PostgreSQL, SQLAlchemy로 만든 게시판 API입니다. Swagger UI에서 회원가입·로그인과 게시글 CRUD를 실행할 수 있습니다. 게시글은 공개 조회가 가능하며, 로그인한 회원만 작성할 수 있습니다. 작성자와 관리자는 게시글을 수정·삭제할 수 있습니다.

## 로컬 실행

Docker와 Compose를 준비한 뒤 `.env.example`을 `.env`로 복사합니다. `POSTGRES_PASSWORD`에는 DB 비밀번호, `JWT_SECRET`에는 최소 32자의 임의 문자열을 입력합니다. JWT 서명 키는 아래 명령으로 생성할 수 있습니다.

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
docker compose up -d --build
docker compose logs -f api
```

- Swagger UI — [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON — [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- DB 연결 상태 — [http://localhost:8000/health](http://localhost:8000/health)

PostgreSQL을 이미 실행 중이라면 `.env`에 연결 정보를 넣고 `uv sync --locked`, `uv run uvicorn app.main:app --reload`로 실행할 수도 있습니다. 애플리케이션이 처음 시작될 때 필요한 테이블을 생성합니다.

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

1. Docker와 Compose가 설치된 EC2 인스턴스에서 제출용 GitHub 저장소를 클론합니다.
2. 인스턴스에서 `.env`를 만들고 배포용 DB 비밀번호와 JWT 키를 입력합니다. `docker compose up -d --build`를 실행한 뒤 `curl -f http://127.0.0.1:8000/health`로 확인합니다.
3. 도메인의 DNS를 EC2 퍼블릭 IP로 연결한 뒤 Caddy 등 HTTPS 리버스 프록시를 설정합니다. API는 호스트의 `127.0.0.1:8000`에 바인딩됩니다. Caddy 설정 예시는 아래와 같습니다.

   ```caddyfile
   api.example.com {
       reverse_proxy 127.0.0.1:8000
   }
   ```

4. EC2 보안 그룹에서 서비스용 TCP 80·443을 허용합니다. SSH를 쓴다면 TCP 22는 접속하는 IP에만 허용합니다. PostgreSQL 포트는 Compose 내부 네트워크에서 사용합니다.
5. 외부 브라우저에서 `https://배포주소/docs`를 열고 회원가입, 로그인, 게시글 CRUD를 확인합니다. 과제에는 GitHub 저장소 URL과 이 Swagger UI URL을 함께 제출합니다.
