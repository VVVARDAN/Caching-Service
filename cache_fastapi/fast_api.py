"""
Required tools for fastapi, db and hashing
"""
from hashlib import md5
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, create_engine, select, Field
from pydantic import BaseModel

# Database setup
DATABASE_URL = "sqlite:///./cache.db"
engine = create_engine(DATABASE_URL, echo=True)

class CachedResult(SQLModel, table=True):
    """
    Model to store cached transformed results to avoid redundant computation.
    """
    id: int = Field(default=None, primary_key=True)
    input_string: str
    transformed_string: str

class Payload(SQLModel, table=True):
    """
    Model to store final processed payloads identified by a unique hash.
    """
    id: int = Field(default=None, primary_key=True)
    identifier: str
    output: str

# Create database tables
SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency function to provide a database session.
    """
    with Session(engine) as session:
        yield session


# Initialize FastAPI application
app = FastAPI()

# Transformer function (Simulating an external service)
def transformer_function(input_string: str) -> str:
    """
    Simulated transformation function. Converts input string to uppercase.
    """
    return input_string.upper()

# Request Model
class PayloadRequest(BaseModel):
    """
    Request model for the /payload endpoint.
    Contains two lists of strings that must have the same length.
    """
    list_1: List[str]
    list_2: List[str]

# Caching function
def get_or_cache_transformation(input_string: str, session: Session) -> str:
    """
    Retrieves a cached transformation if it exists; otherwise, applies the transformation,
    caches it, and returns the result.
    
    Args:
        input_string (str): The input string to be transformed.
        session (Session): Database session for querying and storing cached results.
    
    Returns:
        str: The transformed string.
    """
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
    """
    Creates and stores a new payload based on transformed input lists.
    
    Args:
        request (PayloadRequest): Contains two equal-length lists of strings to be processed.
        session (Session): Database session for storing and retrieving results.
    
    Raises:
        HTTPException: If the two lists are not of the same length.
    
    Returns:
        dict: A dictionary containing the unique identifier of the processed payload.
    """
    if len(request.list_1) != len(request.list_2):
        raise HTTPException(status_code=400, detail="Lists must be of the same length.")
    
    transformed_1 = [get_or_cache_transformation(s, session) for s in request.list_1]
    transformed_2 = [get_or_cache_transformation(s, session) for s in request.list_2]
    
    interleaved_result = ", ".join(sum(zip(transformed_1, transformed_2), ()))
    identifier = md5(interleaved_result.encode()).hexdigest()
    
    existing_payload = session.exec(select(Payload).where(Payload.identifier == identifier)).first()
    if existing_payload:
        return {"identifier": existing_payload.identifier}
    
    new_payload = Payload(identifier=identifier, output=interleaved_result)
    session.add(new_payload)
    session.commit()
    return {"identifier": identifier}

@app.get("/payload/{identifier}")
def read_payload(identifier: str, session: Session = Depends(get_session)):
    """
    Retrieves a stored payload based on its unique identifier.
    
    Args:
        identifier (str): Unique hash identifier of the payload.
        session (Session): Database session for querying stored payloads.
    
    Raises:
        HTTPException: If the payload with the given identifier is not found.
    
    Returns:
        dict: A dictionary containing the stored output.
    """
    payload = session.exec(select(Payload).where(Payload.identifier == identifier)).first()
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found.")
    return {"output": payload.output}
