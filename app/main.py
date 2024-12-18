from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, Task
from .schemas import TaskCreate, TaskUpdate
from .crud import get_tasks, get_task, create_task, update_task, delete_task

# Инициализация базы данных
Base.metadata.create_all(bind=engine)

# Создание FastAPI-приложения
app = FastAPI()

# Подключение шаблонов и статики
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Перенаправление с "/" на список задач
@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    tasks = get_tasks(db)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})




# Список задач
@app.get("/tasks")
def read_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = get_tasks(db)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


# Страница создания задачи
from fastapi import Form  # Импорт для работы с формами

# Форма создания новой задачи
@app.get("/tasks/new", name="create_task_form")
def create_task_form(request: Request):
    return templates.TemplateResponse("create_task.html", {"request": request})

# Обработка формы создания задачи
@app.post("/tasks/new", name="create_task_form_post")
def create_task_post(
        title: str = Form(...),
        description: str = Form(None),
        db: Session = Depends(get_db),
):
    new_task = Task(
        title=title,
        description=description,
        status="todo",
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return RedirectResponse(url="/tasks", status_code=303)



# Просмотр задачи
@app.get("/tasks/{task_id}")
def read_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})


# Страница редактирования задачи
@app.get("/tasks/{task_id}/edit", name="edit_task")
def edit_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})

# Обновление задачи
@app.post("/tasks/{task_id}/edit")
def update_task(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        status: str = Form(...),
        progress: int = Form(...),
        db: Session = Depends(get_db),
):
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Обновляем поля задачи
    task.title = title
    task.description = description
    task.status = status

    # Логика изменения прогресса в зависимости от статуса
    if status == 'to_do':
        task.progress = 0  # Если статус To Do, прогресс обнуляется
    elif status == 'done':
        task.progress = 100  # Если статус Done, прогресс устанавливается на 100%
    elif progress < 100:
        task.progress = progress  # Если статус In Progress, оставить указанный прогресс

    # Если прогресс ниже 100%, статус не может быть Done
    if task.progress < 100 and status == 'done':
        task.status = 'in_progress'

    db.commit()
    return RedirectResponse(url="/", status_code=303)


# Завершить задачу
@app.post("/tasks/{task_id}/complete", name="complete_task")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Обновляем статус и прогресс
    task.status = "done"
    task.progress = 100
    db.commit()
    db.refresh(task)
    return RedirectResponse(url="/", status_code=303)


# Удаление задачи
@app.post("/tasks/{task_id}/delete", name="delete_task")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/tasks", status_code=303)

