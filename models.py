from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Voter(Base):
    __tablename__ = "voters"
    id = Column(Integer, primary_key=True, index=True)
    nid = Column(String(20), unique=True, index=True)        # length 20
    name = Column(String(100), nullable=False)              # length 100
    birth_date = Column(String(10), nullable=False)         # YYYY-MM-DD format
    has_voted = Column(Boolean, default=False)

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)              # length 100
    party = Column(String(50), nullable=False)              # length 50
    votes = relationship("Vote", back_populates="candidate")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(Integer, ForeignKey("voters.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    voter = relationship("Voter")
    candidate = relationship("Candidate", back_populates="votes")


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    pass_field = Column("pass", String(200), nullable=False)  
