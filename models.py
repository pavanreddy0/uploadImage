#!/usr/bin/env python

import os
from datetime import datetime

from dictalchemy import DictableModel
from dotenv import load_dotenv
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

load_dotenv(verbose=True)

Base = declarative_base(cls=DictableModel)

DATABASE = os.getenv("DB_NAME")


class User(UserMixin, Base):
    """Data Model for Resource table"""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("username"),
        {"schema": DATABASE},
    )
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    username = Column(String(64), nullable=True)
    email = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode("utf8")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    created_on = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
    )
    updated_on = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        onupdate=datetime.now,
    )

    def __repr__(self):
        return f"<Resource model {self.id}>"


class Images(Base):
    """Data Model for Resource table"""

    __tablename__ = "images"
    __table_args__ = {"schema": DATABASE}
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column(String(64), nullable=False)
    size = Column(Integer, nullable=False)
    created_on = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
    )
    updated_on = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        onupdate=datetime.now,
    )

    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey(f"{DATABASE}.{User.__tablename__}.id"),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="images")

    def __repr__(self):
        return f"<Resource model {self.id}>"
