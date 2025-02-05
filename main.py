from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import crud, models, schemas, auth
from database import engine, get_db
from auth import get_current_user

app = FastAPI(debug=True)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)  # Include authentication routes

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/todo/")

@app.post("/todo/", response_model=schemas.TodoResponse)
def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)  # Ensure user is an instance of Users model
):
    return crud.create_todo(db, todo, owner_id=user.id)  # Use user.id instead of user["id"]

@app.get("/todo/", response_model=list[schemas.TodoResponse])
def read_todos(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    user: models.Users = Depends(get_current_user)
):
    return crud.get_todos(db, owner_id=user.id, skip=skip, limit=limit)  # Use user.id

@app.get("/todo/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(get_current_user)
):
    return crud.get_todo(db, todo_id, owner_id=user.id)  # Use user.id

@app.put("/todo/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int, 
    todo_update: schemas.TodoUpdate, 
    db: Session = Depends(get_db), 
    user: models.Users = Depends(get_current_user)
):
    return crud.update_todo(db, todo_id, todo_update, owner_id=user.id)  # Use user.id

@app.delete("/todo/{todo_id}", response_model=schemas.TodoResponse)
def delete_todo(
    todo_id: int, 
    db: Session = Depends(get_db), 
    user: models.Users = Depends(get_current_user)
):
    return crud.delete_todo(db, todo_id, owner_id=user.id)  # Use user.id
