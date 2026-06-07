# app.py for FastAPI
from fastapi import FastAPI, UploadFile, File, HTTPException
import joblib
import pdfplumber
import io
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load models
model = joblib.load('resume_classifier_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

app = FastAPI(title="JobScan NLP ML Service")

def predict_domain(text: str) -> str:
    text_lower = text.lower()
    domains = {
        "Data Science & ML": [
            "data science", "machine learning", "deep learning", "python", "statistics", "neural networks", 
            "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "keras", "nlp", "computer vision",
            "predictive modeling", "r programming", "data analysis", "analytics"
        ],
        "Software Engineering": [
            "software engineer", "full stack", "frontend", "backend", "java", "spring boot", "c++", "c#", 
            "javascript", "typescript", "golang", "rust", "software developer", "oop", "algorithms", 
            "data structures", "microservices", "rest api", "system design"
        ],
        "DevOps & Cloud": [
            "devops", "cloud computing", "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", 
            "ci/cd", "terraform", "ansible", "linux", "system administrator", "infrastructure as code"
        ],
        "Data Engineering": [
            "data engineer", "apache spark", "hadoop", "etl", "data warehouse", "redshift", "snowflake", 
            "airflow", "kafka", "sql server", "big data", "data pipeline"
        ],
        "Finance & Accounting": [
            "finance", "accounting", "banking", "ledger", "audit", "taxation", "investment", "portfolio", 
            "equity", "financial analysis", "cfa", "cpa", "excel modeling", "risk management"
        ],
        "Human Resources": [
            "human resources", "hr", "recruitment", "talent acquisition", "onboarding", "payroll", 
            "employee relations", "hiring", "compensation", "benefits", "performance management"
        ],
        "Marketing & Sales": [
            "marketing", "seo", "sales", "social media", "campaign", "digital marketing", "growth hacking", 
            "lead generation", "branding", "public relations", "b2b sales", "crm"
        ],
        "Healthcare & Medicine": [
            "healthcare", "medical", "clinical", "nurse", "patient care", "pharmaceutical", "hospital", 
            "diagnosis", "health information technology", "biomedical"
        ],
        "Legal & Compliance": [
            "legal", "lawyer", "corporate law", "compliance", "litigation", "contract management", 
            "paralegal", "intellectual property", "regulatory affairs"
        ],
        "Product & Project Management": [
            "product manager", "project manager", "scrum", "agile", "pmp", "product roadmap", 
            "stakeholder management", "delivery", "sprint", "kanban"
        ]
    }
    
    scores = {}
    for domain, keywords in domains.items():
        score = 0
        for keyword in keywords:
            score += text_lower.count(keyword)
        scores[domain] = score
        
    max_domain = max(scores, key=scores.get)
    if scores[max_domain] > 0:
        return max_domain
    return "General / Other"

@app.post("/analyze")
async def analyze(resume: UploadFile, jd: UploadFile):
    try:
        # Extract text
        resume_bytes = await resume.read()
        jd_bytes = await jd.read()
        
        resume_text = extract_text(resume_bytes, resume.filename)
        jd_text = extract_text(jd_bytes, jd.filename)
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the resume file.")
        if not jd_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the job description file.")

        # Compute TF-IDF Cosine Similarity for Match Score
        resume_vec = vectorizer.transform([resume_text])
        jd_vec = vectorizer.transform([jd_text])
        similarity = cosine_similarity(resume_vec, jd_vec)[0][0]
        match_score = float(similarity * 100)
        
        # Predict Recommendation using classifier
        combined = resume_text + " " + jd_text
        vec = vectorizer.transform([combined])
        
        pred = model.predict(vec)[0]
        # Translate to string label
        try:
            # Handle if pred is integer index
            recommendation = label_encoder.inverse_transform([int(pred)])[0]
        except Exception:
            # Handle if pred is already a string
            recommendation = str(pred)
            
        # Get Confidence Score
        probs = model.predict_proba(vec)[0]
        try:
            # Find class index
            class_list = list(label_encoder.classes_)
            class_idx = class_list.index(recommendation)
            confidence = float(probs[class_idx] * 100)
        except Exception:
            # Fallback to max probability
            confidence = float(np.max(probs) * 100)
            
        # Predict Domain from resume text
        domain = predict_domain(resume_text)
        
        return {
            "match_score": round(match_score, 2),
            "recommendation": recommendation,
            "domain": domain,
            "confidence": round(confidence, 2)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_text(data, filename):
    if filename.endswith('.pdf'):
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text = " ".join(p.extract_text() or "" for p in pdf.pages)
                if text.strip():
                    return text
        except Exception:
            pass
    # Fallback to decoding as text
    try:
        return data.decode('utf-8')
    except Exception:
        # If UTF-8 fails, try latin-1
        try:
            return data.decode('latin-1')
        except Exception:
            return ""