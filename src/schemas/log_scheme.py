from pydantic import BaseModel

class CreateLog(BaseModel):
    message: str

class ModifyLog(BaseModel):
    message: str | None = None