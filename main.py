from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Voting Machine API")

# Allow all origins (or specify your frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000", "http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],  # <- IMPORTANT: allows OPTIONS
    allow_headers=["*"],  # <- allows Content-Type, Authorization, etc.
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "E-Voting System API is running 🚀"}


@app.post("/voter/register")
def register_voter(voter: schemas.VoterRegister, db: Session = Depends(get_db)):
    existing_voter = db.query(models.Voter).filter(models.Voter.nid == voter.nid).first()
    if existing_voter:
        raise HTTPException(status_code=400, detail="Voter already registered")

    new_voter = models.Voter(nid=voter.nid, name=voter.name, birth_date=voter.birth_date)
    db.add(new_voter)
    db.commit()
    db.refresh(new_voter)
    return {"message": f"Voter {voter.name} registered successfully"}

@app.get("/voter/check/{nid}")
def check_voter_registration(nid: str, db: Session = Depends(get_db)):
    voter = db.query(models.Voter).filter(models.Voter.nid == nid).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not registered")

    return {
        "nid": voter.nid,
        "name": voter.name,
        "birth_date": voter.birth_date,
        "has_voted": voter.has_voted,
        "message": "Voter is registered ✅"
    }

@app.get("/voterlist")
def voter_list(db: Session = Depends(get_db)):
    """
    Returns the list of all registered voters
    """
    voters = db.query(models.Voter).all()
    if not voters:
        return {"message": "No voters registered yet", "voters": []}

    results = []
    for voter in voters:
        results.append({
            "id": voter.id,
            "nid": voter.nid,
            "name": voter.name,
            "birth_date": str(voter.birth_date) if voter.birth_date else None,
            "has_voted": bool(voter.has_voted)
        })

    return {"voters": results}


@app.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Check if a specific candidate exists by ID
    """
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "party": candidate.party
    }

@app.get("/candidates")
def list_candidates(db: Session = Depends(get_db)):
    """
    List all registered candidates with vote counts
    """
    candidates = db.query(models.Candidate).all()
    if not candidates:
        return {"message": "No candidates registered yet", "candidates": []}

    results = []
    for candidate in candidates:
        vote_count = db.query(models.Vote).filter(models.Vote.candidate_id == candidate.id).count()
        results.append({
            "id": candidate.id,
            "name": candidate.name,
            "party": candidate.party,
            "vote_count": vote_count
        })

    return {"candidates": results}






@app.post("/admin/login")
def admin_login(admin: schemas.AdminLogin, db: Session = Depends(get_db)):
    # Search admin by email
    db_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    # If no admin found
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found ❌")

    # If password doesn’t match
    if db_admin.pass_field != admin.password:
        raise HTTPException(status_code=401, detail="Incorrect password ❌")

    # Success
    return {
        "message": "Admin login successful ✅",
        "admin_email": db_admin.email
    }

@app.post("/candidate/add")
def add_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    new_candidate = models.Candidate(name=candidate.name, party=candidate.party)
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {"message": f"Candidate {candidate.name} added successfully"}




@app.post("/vote/{nid}/{candidate_id}")
def vote(nid: str, candidate_id: int, db: Session = Depends(get_db)):
    voter = db.query(models.Voter).filter(models.Voter.nid == nid).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")

    if voter.has_voted:
        raise HTTPException(status_code=400, detail="Voter has already voted")

    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_vote = models.Vote(voter_id=voter.id, candidate_id=candidate.id)
    db.add(new_vote)
    voter.has_voted = True
    db.commit()

    return {"message": f"{voter.name} successfully voted for {candidate.name}"}


@app.get("/results")
def get_results(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).all()
    results = []
    for candidate in candidates:
        vote_count = db.query(models.Vote).filter(models.Vote.candidate_id == candidate.id).count()
        results.append({
            "candidate": candidate.name,
            "party": candidate.party,
            "votes": vote_count
        })
    return {"results": results}
