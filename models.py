from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

    # This allows you to easily access all todos created by the user
    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('user.id'))  # Corrected ForeignKey reference to 'user.id'

    # This relationship allows you to easily access the user who owns the todo
    owner = relationship("Users", back_populates="todos")


