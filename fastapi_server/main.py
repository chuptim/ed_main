import uvicorn
from fastapi import FastAPI, HTTPException, status
from task_storage import TaskStorage
from scheme import STask, STaskAdd


storage = TaskStorage("../tasks.txt")
app = FastAPI(
    title="Трекер Задач",
    description="Task Manager API",
    version="1.1.fastapi"
)


@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_tasks():
    return storage.get_all()


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(task: STaskAdd) -> STask:
    """Добавление задачи"""
    task_dict = task.model_dump()
    task_dict["id"] = storage.next_id()
    new_task = STask(**task_dict)
    storage.add_task(task_dict)
    return new_task


@app.post("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK)
def complete_task(task_id: int):
    if not storage.complete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)





