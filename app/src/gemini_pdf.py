# read pdf papers from pdfs path and generate a paper review
# add the gemini review in the respective json file

import os
import time
import google.generativeai as genai
from app.src.utils import load_env_variables

def collect_gemini_review(skip_others=True):
    load_env_variables()
    import os
    import pandas as pd

    dfs = []

    pdf_folder = os.getenv('PDF_FOLDER')

    for folder in os.listdir(f"{pdf_folder}"):
        if not os.path.isdir(f"{pdf_folder}/{folder}"):
            continue

        if skip_others and folder == '_others':
            continue

        if os.getenv('ENV') == 'DEV':
            print(f'\nProcessing {pdf_folder}/{folder}')

        for file in os.listdir(f"{pdf_folder}/{folder}"):
            if file.endswith('.pdf'):
                # print('\n'.join(get_all_highlights(f"./pdfs/{file}")))
                file_path = f"{pdf_folder}/{folder}/{file}"
                gemini_model_review = ""#gemini_review(file_path)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active.

    Some files uploaded to the Gemini API need to be processed before they can be
    used as prompt inputs. The status can be seen by querying the file's "state"
    field.

    This implementation uses a simple blocking polling loop. Production code
    should probably employ a more sophisticated approach.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()


# get PDF review from Gemini.
def gemini_review(file_path: str):

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    generation_config = {
        "temperature": 0.15,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    # You may need to update the file paths
    files = [
        upload_to_gemini(file_path),
    ]

    # Some files have a processing delay. Wait for them to be ready.
    wait_for_files_active(files)

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "I am a PHD research. ",
                    "My researches consist in determine the tracker losses in PV systems based on the solar plant "
                    "empirical data.\nThe trackers can malfunction and the strings can start to produce less energy once they are not in the proper angle.\nThe data used to determine this losses can be either string currents, tracker angle, or the irradiance merged with the\ninverter AC power. Machine learning models can be useful too.",
                    files[0],
                ],
            },
        ]
    )

    response = chat_session.send_message("Based on this research proposal, review this article. Highlighting it in one or two paragraphs.")
    print(response)
    return response


if __name__ == "__main__":
    collect_gemini_review()

    # TODO: append the review at the search.json db
