from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoResponse

def create_todo(db: Session, todo: TodoCreate, owner_id: int):
    db_todo = Todo(**todo.dict(), owner_id=owner_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todo(db: Session, todo_id: int, owner_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == owner_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

def get_todos(db: Session, owner_id: int, skip: int = 0, limit: int = 10):
    return db.query(Todo).filter(Todo.owner_id == owner_id).offset(skip).limit(limit).all()

def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate, owner_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == owner_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo_update.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int, owner_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == owner_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return db_todo