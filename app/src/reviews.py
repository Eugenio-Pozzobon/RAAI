from typing import List, Tuple
import fitz
import streamlit as st
import os
from app.src.utils import load_env_variables

load_env_variables()

def _parse_highlight(annot: fitz.Annot, wordlist: List[Tuple[float, float, float, float, str, int, int, int]]) -> str:
    points = annot.vertices
    quad_count = int(len(points) / 4)
    sentences = []
    for i in range(quad_count):
        # where the highlighted part is
        r = fitz.Quad(points[i * 4 : i * 4 + 4]).rect

        words = [w for w in wordlist if fitz.Rect(w[:4]).intersects(r)]
        sentences.append(" ".join(w[4] for w in words))
    sentence = " ".join(sentences)
    return sentence


def handle_page(page):
    wordlist = page.get_text("words")  # list of words on page
    wordlist.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x

    highlights = []
    annot = page.first_annot
    while annot:
        if annot.type[0] == 8:
            highlights.append(_parse_highlight(annot, wordlist))
        annot = annot.next
    return highlights


def get_all_highlights(filepath: str, just_first = False) -> List:
    doc = fitz.open(filepath)

    highlights = []
    for page in doc:
        highlights += handle_page(page)
        if just_first:
            break

    return highlights

def get_insert_texts(filepath: str) -> List:
    doc = fitz.open(filepath)
    texts = []
    for page in doc:
        for annot in page.annots():
            if annot.type[1] == 'FreeText':
                texts.append(annot.info["content"])

    return texts



@st.cache_data()
def get_all_reviews(skip_others = True):
    load_env_variables()
    cnt_reviews, cnt_download = 0, 0
    reviews = []
    pdf_folder = os.getenv('PDF_FOLDER')

    pdf_files_path = []

    print(f'\nProcessing {pdf_folder}')
    for dir in os.listdir(f"{pdf_folder}"):

        pdf_files_path.append(f"{pdf_folder}/{dir}")
        if not os.path.isdir(f"{pdf_folder}/{dir}"):
            continue

        if skip_others and dir == '_others':
            continue

        for file in os.listdir(f"{pdf_folder}/{dir}"):
            pdf_files_path.append(f"{pdf_folder}/{dir}/{file}")


    pdf_files_path = [file for file in pdf_files_path if file.endswith('.pdf')]
    for file in pdf_files_path:
        # if file has more than 30 pages, skip it
        doc = fitz.open(f"{file}")
        if len(doc) > 30:
            continue

        highlight = get_all_highlights(file, just_first=True)
        review = get_insert_texts(file)

        reviews.append({
            'title': file.split('/')[-1].replace('.pdf', '').replace('_', ' ').upper(),
            'file': file.split('/')[-1],
            'folder': file.split('/')[-2],
            'absolute_path': os.path.abspath(file),
            'review': review,
            'has_review': True if review != [] else False,
            'has_file': True,
            'has_read': True if highlight != [] else False,
        })
        cnt_reviews += 1 if review != [] else 0
        cnt_download += 1

    if os.getenv('ENV') == 'DEV':
        print(f"Total downloads: {cnt_download}")
        print(f"Total reviews: {cnt_reviews}")

    # list all reviews
    # for review in reviews:
    #     if review['has_file']:
    #         print(f"\n{review['title']}")
    #         print(f"\t- Has review: {review['has_review']}", f"\t- Has file: {review['has_file']}")

    return reviews
