from pydantic import BaseModel

class VoterRegister(BaseModel):
    nid: str
    name: str
    birth_date: str

class CandidateCreate(BaseModel):
    name: str
    party: str

class AdminLogin(BaseModel):
    email: str
    password: str