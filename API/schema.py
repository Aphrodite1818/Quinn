#============================================================#
#              RENDER DATABASE SCHEMAS                       #
#============================================================#

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------------------------------------------------#
#                   USER SCHEMAS
# ---------------------------------------------------#

class UserBase(BaseModel):
    email: str


class CreateUser(UserBase):
    password: str


class UpdateUser(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------#
#                  SESSION SCHEMAS
# ---------------------------------------------------#

class SessionBase(BaseModel):
    user_id: int


class CreateSession(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------#
#               MESSAGE SCHEMAS
# ---------------------------------------------------#

class MessageBase(BaseModel):
    session_id: int
    role: str
    content: str


class CreateMessage(MessageBase):
    pass


class UpdateMessage(BaseModel):
    content: Optional[str] = None


class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------#
#               BULK OPERATIONS
# ---------------------------------------------------#

class BulkCreateMessages(BaseModel):
    messages: List[CreateMessage]


class BulkDeleteMessages(BaseModel):
    message_ids: List[int]


# ---------------------------------------------------

if __name__ == "__main__":
    print("Schema module loaded")