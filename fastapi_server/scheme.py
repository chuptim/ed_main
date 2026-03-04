from pydantic import BaseModel, Field, field_validator

class STaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        title="Название задачи",
        description="""При добавлении задачи пользователь указывает её название 
        (размер от 2 до 100 символов)"""
    )
    priority: str = Field(
        ...,
        title="Приоритет задачи",
        description="""Пользователь указывает приоритет задачи **high**, **normal**, **low** 
        вне зависимости от регистра"""
    )
    isDone: bool = Field(
        default=False,
        title="Статус выполнения",
        description="По дефолту **False**"
    )

    @field_validator('priority', mode='before')
    @classmethod
    def validate_priority(cls, value):
        if not isinstance(value, str):
            raise ValueError("Приоритет должен быть строкой")
        value = value.lower()
        allowed = {"high", "normal", "low"}
        if value not in allowed:
            raise ValueError(f"Приоритет должен быть одним из: {', '.join(sorted(allowed))}")
        return value


class STaskAdd(STaskBase):
    pass


class STask(STaskBase):
    id: int = Field(
        ...,
        title="ID задачи",
        description="Уникальный идентификатор. Формируется автоматически, начиная с 1"
    )