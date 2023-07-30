# llm-tutor
An LLM-powered tutoring frontend for Q&amp;Aing learning materials.


# Basic usage
**DISCLAIMER: This repo is work in process, there is no clean containered release yet.**
## Manual testing
0. Install Anaconda or Miniconda
1. Create Conda environment based on Python 3.10 (e.g. "conda create -y -k --prefix venv python=3.10)
2. Activate the Conda environment (e.g. "conda activate venv/)
3. Download, build and install the appropriate cuda-enabled pytorch packages (e.g. "conda install -y -k pytorch[version=2,build=py3.10_cuda11.7*] torchvision torchaudio pytorch-cuda=11.7 cuda-toolkit ninja git -c pytorch -c nvidia/label/cuda-11.7.0 -c nvidia")
4. Install the pip requirements ("pip install -r requirements.txt")
5. start the backend (e.g. "python start_backend.py") - the FastAPI-Backend, via which LLM and vectorstore functinality is accessed. The backend can already be accessed via the logged uvicorn URL + /docs (Swagger UI)
6. start the streamlit app(s) (e.g. "streamlit run streamlit_main.py") - the streamlit prototype app(s) will be started and a browser window should automatically open
7. (optional) start the umbrella flask app (e.g. "python flask_main.py") - the flask app which integrates the streamlit apps will be started and can be accessed via the logged URL


# Rough plan
## Features
- load and embed learning resources
- interface embedded resources via LLMs
    - ask questions
    - hold conversation
    - create and work through learning cards
    - access web search results via LLM tool
## Main components
- backend for
    - loading and interfacing LLMs
    - loading and interfacing vectorstore-based knowledgebases
- frontend by
    - prototyping simple streamlit apps for the given features
    - integrating streamlit apps in flask app
## TODO
- ~~implement control structures~~
- ~~extract common functionality to utility~~
- ~~implement streamlit app prototype~~
- ~~clean up control structures and utility~~
- clean up streamlit app
- ~~clean up interface~~
- parameterize backend interface
- ~~add and adjust Common Flask Frontend~~
- ~~integrate streamlit into Common Flask Frontend (iframes)~~
- add parameterized model loading for different types to utility
    - read in available local models and interface
    - allow for downloading and storing models from Huggingface
- add resource-monitoring and guards for resource-heavy functionality
- add finetuning utility
- clean up flask app