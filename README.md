# 🧠 AI Resume Fraud Detector

An AI-powered backend system that analyzes resumes to detect exaggeration or fraudulent claims using NLP and machine learning techniques.

---

## 🚀 Features

- 📄 Upload and parse PDF resumes
- 🧠 NLP-based skill extraction using spaCy
- 📊 ML-based text similarity scoring (TF-IDF + Cosine Similarity)
- ⚠️ Fraud risk classification (GENUINE / SUSPICIOUS / FAKE)
- 🧑‍💻 GitHub profile verification for claimed skills
- 🗄️ Stores results in SQLite database
- 🔌 REST API with Swagger documentation (FastAPI)

---

## 🛠 Tech Stack

- **Backend:** FastAPI  
- **NLP:** spaCy  
- **ML:** scikit-learn (TF-IDF + Cosine Similarity)  
- **PDF Parsing:** PyMuPDF  
- **Database:** SQLite + SQLAlchemy  
- **API Docs:** Swagger UI  
- **Language:** Python 3  

---

## 📂 Project Structure

```
backend/
│── main.py
│── requirements.txt
│── resumes.db
│── start.sh
```

---

## ▶️ Run Locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
uvicorn main:app --reload
```

Open in browser:
```
http://127.0.0.1:8000/docs
```

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|------|---------|------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload resume PDF |
| GET | `/candidates` | View analyzed resumes |

---

## 📈 Sample Output

```json
{
  "skills": ["python", "sql"],
  "fraud_score": 42.5,
  "risk": "SUSPICIOUS",
  "github_confidence": 0.6
}
```

---

## 🎯 Use Cases

- HR resume screening
- Fraud detection in recruitment
- Skill verification pipelines
- AI-assisted hiring systems

---

## 👨‍💻 Author

**Haripad Patar**  
Computer Science | AI & Backend Development
