from app.models import Task
from tortoise.exceptions import DoesNotExist
from datetime import datetime


# Получить все задачи
async def get_tasks(skip: int = 0, limit: int = 0):
    query = Task.all().offset(skip)
    if limit > 0:
        query = query.limit(limit)
    return await query


# Получить задачу по ID
async def get_task(task_id: int):
    try:
        return await Task.get(id=task_id)  # Получаем задачу по id асинхронно
    except DoesNotExist:
        return None  # Если задача не найдена, возвращаем None


# Фильтр задач по статусу
async def get_tasks_by_status(status: str, skip: int = 0, limit: int = 10):
    return await Task.filter(status=status).offset(skip).limit(limit)


# Подсчет всех задач
async def count_tasks():
    return await Task.all().count()


# Подсчет задач по статусу
async def count_tasks_by_status(status: str):
    return await Task.filter(status=status).count()


# Создание новой задачи
async def create_task(title: str, description: str, status: str, progress: int = 0):
    task = await Task.create(
        title=title,
        description=description,
        status=status,
        progress=progress
    )
    print(f"Created task: {task}")  # Выводим информацию о задаче в консоль
    return task


# Обновить существующую задачу
async def update_task(task_id: int, title: str, description: str, status: str, progress: int):
    task = await Task.filter(id=task_id).first()
    if not task:
        return None  # Возврат, если задача не найдена

    # Обновляем поля задачи
    task.title = title
    task.description = description
    task.status = status

    # Логика изменения прогресса в зависимости от статуса
    if status == 'to_do':
        task.progress = 0
    elif status == 'done':
        task.progress = 100
    elif progress < 100:
        task.progress = progress

    # Если прогресс ниже 100%, статус не может быть Done
    if task.progress < 100 and status == 'done':
        task.status = 'in_progress'

    # Сохраняем изменения
    await task.save()
    return task


# Удалить задачу
async def delete_task(task_id: int):
    task = await get_task(task_id)
    if not task:
        return None  # Если задача не найдена, возвращаем None
    await task.delete()  # Удаляем задачу асинхронно
    return task
