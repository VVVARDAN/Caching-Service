from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from pydantic import BaseModel
from typing import List
import hashlib
from sqlmodel import Field

# Database setup
database_url = "sqlite:///./cache.db"
engine = create_engine(database_url, echo=True)

class CachedResult(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    input_string: str
    transformed_string: str

class Payload(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    identifier: str
    output: str
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

# Transformer function (Simulating an external service)
def transformer_function(input_string: str) -> str:
    return input_string.upper()

# Request Model
class PayloadRequest(BaseModel):
    '''Request Model'''
    list_1: List[str]
    list_2: List[str]

# Caching function
def get_or_cache_transformation(input_string: str, session: Session) -> str:
    existing_entry = session.exec(select(CachedResult).where(CachedResult.input_string == input_string)).first()
    if existing_entry:
        return existing_entry.transformed_string
    transformed_string = transformer_function(input_string)
    new_entry = CachedResult(input_string=input_string, transformed_string=transformed_string)
    session.add(new_entry)
    session.commit()
    return transformed_string

@app.post("/payload")
def create_payload(request: PayloadRequest, session: Session = Depends(get_session)):
    if len(request.list_1) != len(request.list_2):
        raise HTTPException(status_code=400, detail="Lists must be of the same length.")
    
    transformed_1 = [get_or_cache_transformation(s, session) for s in request.list_1]
    transformed_2 = [get_or_cache_transformation(s, session) for s in request.list_2]
    
    interleaved_result = ", ".join(sum(zip(transformed_1, transformed_2), ()))
    identifier = hashlib.md5(interleaved_result.encode()).hexdigest()
    
    existing_payload = session.exec(select(Payload).where(Payload.identifier == identifier)).first()
    if existing_payload:
        return {"identifier": existing_payload.identifier}
    
    new_payload = Payload(identifier=identifier, output=interleaved_result)
    session.add(new_payload)
    session.commit()
    return {"identifier": identifier}

@app.get("/payload/{identifier}")
def read_payload(identifier: str, session: Session = Depends(get_session)):
    payload = session.exec(select(Payload).where(Payload.identifier == identifier)).first()
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found.")
    return {"output": payload.output}


if __name__ == "__main__":
    print(1)