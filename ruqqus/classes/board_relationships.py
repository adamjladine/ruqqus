from ruqqus.helpers.base36 import *
from ruqqus.helpers.security import *
from sqlalchemy import *
from ruqqus.__main__ import Base, db, cache
import time

class ModRelationship(Base):
    __tablename__ = "mods"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    board_id = Column(BigInteger, ForeignKey("boards.id"))
    created_utc = Column(BigInteger, default=0)

    def __init__(self, *args, **kwargs):
        if "created_utc" not in kwargs:
            kwargs["created_utc"] = int(time.time())

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Mod(id={self.id}, uid={self.uid}, board_id={self.board_id})>"


class BanRelationship(Base):

    __tablename__="bans"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    board_id = Column(BigInteger, ForeignKey("boards.id"))
    created_utc = Column(BigInteger, default=0)

    def __init__(self, *args, **kwargs):
        if "created_utc" not in kwargs:
            kwargs["created_utc"] = int(time.time())

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Mod(id={self.id}, uid={self.uid}, board_id={self.board_id})>"