from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests

from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

KNOWN_SKILLS = ["python","java","sql","ml","ai","react","node","c++","aws","docker"]

# Database
engine = create_engine("sqlite:///resumes.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class ResumeDB(Base):
    __tablename__ = "resumes"
    id = Column(String, primary_key=True)
    skills = Column(String)
    companies = Column(String)
    fraud_score = Column(Float)
    risk = Column(String)

Base.metadata.create_all(engine)

# GitHub verification
def verify_github(username, skills):
    url = f"https://api.github.com/users/{username}/repos"
    try:
        repos = requests.get(url).json()
    except:
        return [], skills, 0

    found = set()
    for repo in repos:
        text = (repo["name"] + " " + str(repo.get("description",""))).lower()
        for s in skills:
            if s in text:
                found.add(s)

    missing = set(skills) - found
    confidence = len(found) / max(1, len(skills))
    return list(found), list(missing), round(confidence, 2)

# Upload & analyze resume
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    pdf = fitz.open(stream=await file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()

    doc = nlp(text)
    skills = set()
    companies = set()

    for ent in doc.ents:
        if ent.label_ == "ORG":
            companies.add(ent.text)

    for token in doc:
        if token.text.lower() in KNOWN_SKILLS:
            skills.add(token.text.lower())

    resume_vec = model.encode([text])
    template = "Experienced software engineer with strong skills in Python Java and machine learning"
    template_vec = model.encode([template])

    similarity = cosine_similarity(resume_vec, template_vec)[0][0]
    fraud_score = (max(0, len(skills) - 5) * 10) + (similarity * 50)

    if fraud_score > 60:
        risk = "FAKE"
    elif fraud_score > 30:
        risk = "SUSPICIOUS"
    else:
        risk = "GENUINE"

    # GitHub check
    github_user = "haripadpatar"
    verified, missing, gh_conf = verify_github(github_user, list(skills))

    # Save to database
    db = Session()
    record = ResumeDB(
        id=file.filename,
        skills=",".join(skills),
        companies=",".join(companies),
        fraud_score=float(fraud_score),
        risk=risk
    )
    db.add(record)
    db.commit()

    return {
        "skills": list(skills),
        "companies": list(companies),
        "similarity": round(float(similarity), 2),
        "fraud_score": round(float(fraud_score), 2),
        "risk": risk,
        "github_verified_skills": verified,
        "github_missing_skills": missing,
        "github_confidence": gh_conf
    }

# HR dashboard API
@app.get("/candidates")
def get_candidates():
    db = Session()
    records = db.query(ResumeDB).all()
    return [
        {
            "id": r.id,
            "skills": r.skills.split(",") if r.skills else [],
            "companies": r.companies.split(",") if r.companies else [],
            "fraud_score": r.fraud_score,
            "risk": r.risk
        }
        for r in records
    ]
