# Welcome to the RAAI: Research Assistant based on Artificial Intelligent

This project is a simple implementation of a research assistant that can help you with your research. 
It can help you with the following tasks:

1. Search for papers on a given topics/keywords
2. Identify the most relevant papers given your research context
3. Provide tools that enables you to organize your paper review process.

## First steps:
To get started with the research assistant, you need to install the required software and packages. 
First, ensure that you have Python installed on your machine. You can download Python from the official website: https://www.python.org/downloads/

Last, execute the main.bat file if on Windows or main.command if on MacOS. 

This will install all the required packages and start the assistant.

The terminal window should open, and you must not close it. The assistant will run on this terminal window, oppening 
a web interface at your default browser.

## How to use the research assistant:
- The python scripts provide a simple web interface that you can use to interact with the assistant. 
- First, at Keyword page: You can search for papers by entering groups of keywords topics of your research. I 
  recommend to limit each search 
  in 4 keywords. 3 keywords in a group will be very effective. On the other hand, 2 or less keywords will find too 
  many papers, taking too long to process. 
- Second, at Mining page: The assistant will process your keywords and search for papers that matches.
- Third, at Context page: For each keyword group, define the context of your research by providing a brief 
  description of your research on 
  that keywords
- Finally, at Analysis page: Google Gemini will slowly process all the search results and apply a grade of relevance to 
  each paper. 
  This process work evaluating the title and abstract of each paper and comparing with the provided context of your 
  research. Thus, it is important to provide a good description context for each keyword group.
- At the main application page you can navigate through the papers and download the ones that you find relevant.
- The filter tools enable you to map the papers that you have downloaded, read and reviewed, and organize your review 
  process.

# Folder structure and files:
In order to the system identify read and downloaded papers:

- It is mandatory that all the PDF files are stored in the folder `pdfs/` in the root directory of the project.
Inside the `pdfs/` folder, you can create subfolders to organize your papers, but no more than 1 folder level. The 
assistant will automatically find all the PDF files in the `pdfs/` folder and its subfolders.
- Keep the pdf file name as the title of the paper. The assistant will use the pdf file name to identify the paper.

- Also, the assistant will create a bibtex file inside the `bibtex/` folder. There will be all bibtex entries for all 
the downloaded papers inside the `pdfs/` folder.

- Warning: do not modify any other files in the project, as it may break the assistant.

- Although it is not mandatory, I recommend that you use a file manager like git to keep track of the changes in the 
files.

## Limitations:
- The assistant is limited to IEEE, arXiv and Scopus papers.
- The assistant is limited to use the Google Gemini LLM model to evaluate the relevance of the papers.
- You can manually find papers from others databases and add than at the main application page. That way, you can 
  organize your review process without limitation from the supported databases.  

## Future work:
I will be adding more features to the research assistant. Some of the features that we are planning to add are:
1. Summarize and Extract the most important information from a paper given its PDF
2. Generate a summary of a research topic based on all the papers that you have downloaded
3. Maps the papers citations to identify when the bibliographic references are starting to repeat itself, indicating 
   that you have reached a saturation point in your research.
4. Allow custom setup of model and search engine to use in the assistant.
