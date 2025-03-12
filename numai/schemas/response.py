from pydantic import BaseModel

class ResponseModel(BaseModel):
    raw_value: str
    context: str
    modifier: str
    interpreted_value: int
    page_number: int
    table_name: str