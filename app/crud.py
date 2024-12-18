from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Task
from .schemas import TaskCreate, TaskUpdate
from datetime import datetime

# Получить все задачи
def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Task).offset(skip).limit(limit).all()


# Получить задачу по ID
def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


# Фильтр задач по статусу
def get_tasks_by_status(db: Session, status: str, skip: int = 0, limit: int = 10):
    return db.query(Task).filter(Task.status == status).offset(skip).limit(limit).all()


# Подсчет всех задач
def count_tasks(db: Session):
    return db.query(Task).count()


# Подсчет задач по статусу
def count_tasks_by_status(db: Session, status: str):
    return db.query(Task).filter(Task.status == status).count()


## Создание новой задачи
def create_task(db: Session, task: TaskCreate):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        progress=task.progress
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    print(f"Created task: {db_task}")  # Выводим информацию о задаче в консоль
    return db_task



# Обновить существующую задачу
def update_task(db: Session, task_id: int, task: TaskUpdate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db_task.title = task.title
        db_task.description = task.description
        db_task.status = task.status
        db_task.progress = task.progress

        # Меняем статус на 'in progress', если прогресс больше 0
        if db_task.progress > 0 and db_task.status != 'in_progress':
            db_task.status = 'in_progress'

        # Если прогресс 100%, статус меняется на 'done'
        if db_task.progress == 100:
            db_task.status = 'done'

        db.commit()
        db.refresh(db_task)
    return db_task


# Удалить задачу
def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None  # Задача не найдена
    try:
        db.delete(db_task)
        db.commit()
        return db_task
    except SQLAlchemyError as e:
        db.rollback()
        raise e
