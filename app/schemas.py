from pydantic import BaseModel
from typing import Optional


# Схема для базовой задачи
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    progress: int


# Схема для создания задачи (пока ничего не меняется)
class TaskCreate(TaskBase):
    pass


# Схема для обновления задачи (так же может быть без изменений)
class TaskUpdate(TaskBase):
    pass


# Схема для отображения задачи
class Task(TaskBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
