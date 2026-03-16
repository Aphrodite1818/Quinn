#============================================================#
#              MODELS FOR THE DATABASE                        #
#============================================================#



from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# ---------------------------------------------------#
#                   USER MODEL
# ---------------------------------------------------#

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    # relationship
    sessions = relationship("Session", back_populates="user")


# ---------------------------------------------------#
#                   SESSION MODEL
# ---------------------------------------------------#

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")


# ---------------------------------------------------#
#               MESSAGE MODEL
# ---------------------------------------------------#

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("sessions.id"))

    role = Column(String)  # user / assistant / system
    content = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # relationship
    session = relationship("Session", back_populates="messages")


# ---------------------------------------------------

if __name__ == "__main__":
    print("Database models loaded")