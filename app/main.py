from fastapi import FastAPI, Depends, HTTPException, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
# from app.crud import get_tasks, get_task, get_tasks_by_status, create_task, update_task, delete_task, \
#     count_tasks, count_tasks_by_status  # Импортируем из crud.py
from app.models import Task
from app.crud import *
from fastapi import Form
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from tortoise import Tortoise
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Создание FastAPI-приложения
app = FastAPI()

# Подключение шаблонов и статики
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Инициализация базы данных через Tortoise
@app.on_event("startup")
async def init():
    # Подключение к базе данных и инициализация Tortoise ORM
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',  # URL базы данных, можно использовать другие базы
        modules={'models': ['app.models']}  # Укажите путь к моделям
    )
    # Миграции (если они нужны)
    await Tortoise.generate_schemas()


@app.on_event("shutdown")
async def close():
    # Закрытие подключения при завершении работы приложения
    await Tortoise.close_connections()


# Регистрируем Tortoise ORM с FastAPI
register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['app.models']},  # Укажите путь к моделям
    generate_schemas=True,  # Генерировать схемы при старте приложения
    add_exception_handlers=True
)


# Перенаправление с "/" на список задач
@app.get("/")
async def index(request: Request):
    tasks = await get_tasks()  # Используем асинхронный метод Tortoise
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


# Список задач
@app.get("/tasks")
async def read_tasks(request: Request):
    tasks = await get_tasks()  # Используем асинхронный метод Tortoise
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


# Страница создания задачи
@app.get("/tasks/new", name="create_task_form")
def create_task_form(request: Request):
    return templates.TemplateResponse("create_task.html", {"request": request})


# Обработка формы создания задачи
@app.post("/tasks/new", name="create_task_form_post")
async def create_task_post(
        title: str = Form(...),
        description: str = Form(None),
):
    new_task = await create_task(title, description)  # Используем функцию из crud.py
    return RedirectResponse(url="/tasks", status_code=303)


# Просмотр задачи
@app.get("/tasks/{task_id}")
async def read_task(task_id: int, request: Request):
    task = await get_task(task_id)  # Используем асинхронную функцию для получения задачи
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})


# Страница редактирования задачи
@app.get("/tasks/{task_id}/edit", name="edit_task")
# @app.post("/tasks/{task_id}/edit", name="update_task")
async def edit_task(task_id: int, request: Request):
    task = await get_task(task_id)  # Используем асинхронную функцию для получения задачи
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})


# Обновление задачи
@app.post("/tasks/{task_id}/edit")
async def update_task(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        status: str = Form(...),
        progress: int = Form(...),
):
    task = await get_task(task_id)  # Вызов функции из crud.py
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Логика обновления задачи
    task.title = title
    task.description = description
    task.status = status
    task.progress = progress if status != "done" else 100

    await task.save()  # Сохранение через Tortoise ORM
    return RedirectResponse(url="/", status_code=303)


# Завершить задачу
@app.post("/tasks/{task_id}/complete", name="complete_task")
async def complete_task(task_id: int):
    task = await get_task(task_id)  # Получаем задачу асинхронно
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "done"
    task.progress = 100
    await task.save()  # Сохраняем изменения асинхронно
    return RedirectResponse(url="/", status_code=303)


# Удаление задачи
@app.post("/tasks/{task_id}/delete", name="delete_task")
async def delete_task(task_id: int):
    task = await get_task(task_id)  # Получаем задачу асинхронно
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_task(task_id)  # Используем функцию из crud.py
    return RedirectResponse(url="/tasks", status_code=303)


# Получить задачи по статусу
@app.get("/tasks/status/{status}")
async def read_tasks_by_status(
        status: str, skip: int = Query(0), limit: int = Query(10)
):
    tasks = await get_tasks_by_status(status, skip=skip, limit=limit)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found with this status")
    return tasks


# Подсчитать все задачи
@app.get("/tasks/count")
async def get_task_count():
    total_tasks = await count_tasks()
    return {"total_tasks": total_tasks}


# Подсчитать задачи по статусу
@app.get("/tasks/status/{status}/count")
async def get_task_count_by_status(status: str):
    count = await count_tasks_by_status(status)
    return {"status": status, "count": count}
