from pydantic import BaseModel


class Robot(BaseModel):

    id:str

    x:int
    y:int

    battery:int

    busy:bool=False