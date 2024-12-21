from tortoise import Tortoise
from datetime import datetime
from tortoise import fields
from tortoise.models import Model


class Task(Model):
    id = fields.IntField(pk=True)  # Поле для первичного ключа
    title = fields.CharField(max_length=255, null=False)  # Строка с максимальной длиной
    description = fields.TextField(null=True)  # Текстовое поле
    status = fields.CharField(max_length=20, default="todo", null=False)  # Строка с дефолтным значением
    created_at = fields.DatetimeField(default=datetime.utcnow, null=False)  # Дата и время создания
    updated_at = fields.DatetimeField(default=datetime.utcnow, on_update=datetime.utcnow,
                                      null=False)  # Дата и время обновления
    progress = fields.IntField(default=0, null=False)  # Целочисленное поле для прогресса

    class Meta:
        table = "tasks_task"  # Задаем название таблицы


# Функция для инициализации Tortoise ORM
async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',  # Путь к вашей базе данных
        modules={'models': ['app.models']}  # Путь к моделям
    )
    await Tortoise.generate_schemas()  # Генерация схем
