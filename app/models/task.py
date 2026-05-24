from pydantic import BaseModel


class Task(BaseModel):

    id:str

    x:int
    y:int

    priority:int