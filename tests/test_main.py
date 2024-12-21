import pytest
from app.crud import get_tasks
from app.models import Task
from tortoise.contrib.test import finalizer, initializer

# Фикстура для инициализации базы данных перед тестами
@pytest.fixture(scope="module", autouse=True)
def initialize_tests():
    initializer(["app.models"])  # Указываем путь к моделям
    yield
    finalizer()

@pytest.mark.asyncio
async def test_get_tasks_no_tasks():
    """Тест для случая, когда в базе данных нет задач"""
    tasks = await get_tasks()
    assert tasks == []  # Ожидаем, что вернётся пустой список

@pytest.mark.asyncio
async def test_get_tasks_with_data():
    """Тест для проверки получения задач из базы данных"""
    # Создаем тестовые данные
    task1 = await Task.create(title="Test Task 1", description="Description 1", status="to_do", progress=0)
    task2 = await Task.create(title="Test Task 2", description="Description 2", status="in_progress", progress=50)

    # Получаем все задачи
    tasks = await get_tasks()
    assert len(tasks) == 2  # Ожидаем, что вернётся 2 задачи
    assert tasks[0].title == "Test Task 1"
    assert tasks[1].title == "Test Task 2"

@pytest.mark.asyncio
async def test_get_tasks_with_limit():
    """Тест для проверки ограничения числа возвращаемых задач"""
    # Получаем только одну задачу
    tasks = await get_tasks(limit=1)
    assert len(tasks) == 1  # Ожидаем, что вернётся только одна задача

@pytest.mark.asyncio
async def test_get_tasks_with_skip():
    """Тест для проверки пропуска задач"""
    # Пропускаем первую задачу
    tasks = await get_tasks(skip=1)
    assert len(tasks) == 1  # Ожидаем, что останется только одна задача
    assert tasks[0].title == "Test Task 2"
