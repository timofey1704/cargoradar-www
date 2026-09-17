from pydantic import BaseModel, ConfigDict

class FAQRead(BaseModel):
    """Данные по FAQ для главной"""
    
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)
    
