from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from .github_event import GithubEvent
