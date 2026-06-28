from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import os
import logging
import tempfile
from pdf import PDFHandler
from github import fetch_and_display_github_info
from score import find_profile, _evaluate_resume

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)5s - %(lineno)5d - %(funcName)33s - %(levelname)5s - %(message)s",
)

app = FastAPI()


# Fonction métier : prend un chemin, inchangée ──────────────────────
def evaluate_resume_to_json(pdf_path: str, q: str | None = None):
    logger.debug("Extracting data from PDF")
    pdf_handler = PDFHandler()
    resume_data = pdf_handler.extract_json_from_pdf(pdf_path)
    if resume_data is None:
        return None
    profiles = []
    if hasattr(resume_data, "basics") and resume_data.basics:
        profiles = resume_data.basics.profiles or []
    github_data = {}
    github_profile = find_profile(profiles, "Github")
    if github_profile and github_profile.url:
        github_data = fetch_and_display_github_info(github_profile.url)
    score = _evaluate_resume(resume_data, github_data)
    return {"score": score}


# Route POST : reçoit le fichier, écrit un temp, appelle la fonction ──
@app.post("/evaluate")
def evaluate(file: UploadFile = File(...), secteur: str = Form(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Seuls les PDF sont acceptés")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = evaluate_resume_to_json(tmp_path, secteur)
    finally:
        os.remove(tmp_path)

    if result is None:
        raise HTTPException(status_code=422, detail="CV illisible")
    return result


# Frontend Vue sur "/" 
app.frontend("/", directory="static", fallback="index.html")