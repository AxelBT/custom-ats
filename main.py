from fastapi import FastAPI
import os
import sys
import json
import logging
import csv
from pdf import PDFHandler
from github import fetch_and_display_github_info
from models import JSONResume, EvaluationData
from typing import List, Optional, Dict
from evaluator import ResumeEvaluator
from pathlib import Path
from prompt import DEFAULT_MODEL, MODEL_PARAMETERS
from transform import (
    transform_evaluation_response,
    convert_json_resume_to_text,
    convert_github_data_to_text,
    convert_blog_data_to_text,
)
from config import DEVELOPMENT_MODE

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)5s - %(lineno)5d - %(funcName)33s - %(levelname)5s - %(message)s",
)

app = FastAPI()


app.frontend("/", directory="static", fallback="index.html")

@app.post("/evaluate")
def evaluate_resume_to_json(pdf_path: str , q: str | None = None):

    resume_data = None
    score = 0
    logger.debug(
            f"Extracting data from PDF"
        )
    pdf_handler = PDFHandler()
    resume_data = pdf_handler.extract_json_from_pdf(pdf_path)

    if resume_data == None:
        return None
    return {score}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}