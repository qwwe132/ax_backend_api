import os
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient


class BoardIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get("POSTGRES_DB", "").endswith("_test"):
            raise unittest.SkipTest("POSTGRES_DB must point to a dedicated *_test database.")

    def test_auth_and_post_crud(self):
        from app.shared.config import settings
        from app.shared.db import SessionLocal
        from app.main import app
        from app.users.infrastructure.models import User
        from app.shared.security import issuer

        with TestClient(app) as client:
            self.assertEqual(client.get("/health").json(), {"status": "ok"})
            self.assertEqual(client.get("/docs").status_code, 200)
            spec = client.get("/openapi.json").json()
            self.assertIn("/posts/{post_id}", spec["paths"])
            self.assertIn("OAuth2PasswordBearer", spec["components"]["securitySchemes"])

            credentials = {"username": "writer_" + uuid4().hex[:12], "password": "test-passphrase"}
            created_user = client.post("/auth/signup", json=credentials)
            self.assertEqual(created_user.status_code, 201, created_user.text)
            self.assertEqual(created_user.json()["role"], "member")
            self.assertNotIn("password_hash", created_user.json())
            self.assertEqual(client.post("/auth/signup", json=credentials).status_code, 409)
            self.assertEqual(client.post("/auth/login", data={**credentials, "password": "wrong"}).status_code, 401)

            with SessionLocal() as db:
                account = db.get(User, created_user.json()["id"])
                self.assertTrue(account.password_hash.startswith("$argon2id$"))
                self.assertNotEqual(account.password_hash, credentials["password"])

            login = client.post("/auth/login", data=credentials)
            self.assertEqual(login.status_code, 200, login.text)
            writer = {"Authorization": "Bearer " + login.json()["access_token"]}
            self.assertEqual(client.get("/auth/me", headers=writer).json(), created_user.json())
            now = datetime.now(timezone.utc)
            expired = jwt.encode(
                {"sub": str(created_user.json()["id"]), "iss": issuer,
                 "iat": now - timedelta(minutes=2), "exp": now - timedelta(minutes=1)},
                settings.jwt_secret.get_secret_value(),
                algorithm="HS256",
            )
            self.assertEqual(
                client.get("/auth/me", headers={"Authorization": "Bearer " + expired}).status_code,
                401,
            )

            other = {**credentials, "username": "reader_" + uuid4().hex[:12]}
            other_user = client.post("/auth/signup", json=other)
            self.assertEqual(other_user.status_code, 201, other_user.text)
            other_token = client.post("/auth/login", data=other).json()["access_token"]
            reader = {"Authorization": "Bearer " + other_token}

            payload = {"title": "첫 게시글", "content": "테스트 본문"}
            self.assertEqual(client.post("/posts", json=payload).status_code, 401)
            self.assertEqual(client.post("/posts", headers=writer, json={**payload, "title": " "}).status_code, 422)
            created = client.post("/posts", headers=writer, json=payload)
            self.assertEqual(created.status_code, 201, created.text)
            path = created.headers["location"]
            self.assertEqual(client.get(path).json()["author_id"], created_user.json()["id"])
            self.assertEqual(client.get("/posts?limit=1").json()[0]["id"], created.json()["id"])
            self.assertEqual(client.put(path, headers=reader, json=payload).status_code, 403)
            self.assertEqual(client.delete(path, headers=reader).status_code, 403)

            changed = client.put(path, headers=writer, json={**payload, "title": "수정된 게시글"})
            self.assertEqual(changed.status_code, 200, changed.text)
            self.assertEqual(client.get(path).json()["title"], "수정된 게시글")
            self.assertEqual(client.delete(path, headers=writer).status_code, 204)
            self.assertEqual(client.get(path).status_code, 404)

            extra_post = client.post("/posts", headers=writer, json=payload)
            self.assertEqual(extra_post.status_code, 201)
            with SessionLocal.begin() as db:
                db.get(User, other_user.json()["id"]).role = "admin"
            self.assertEqual(client.delete(extra_post.headers["location"], headers=reader).status_code, 204)
