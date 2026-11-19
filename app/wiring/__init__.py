from fastapi import FastAPI

from . import posts, users


def wire_dependencies(app: FastAPI) -> None:
    users.wire_dependencies(app)
    posts.wire_dependencies(app)
