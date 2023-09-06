# LLM Tutor

## Code entrypoints:
- `src/interfaces/backend_interface.py` holds the main FastAPI backend
- `src/interfaces/client_interface.py` will hold a client representation
- `src/utility/` holds hierarchical utility scripts (from bronze~general to gold~specific)

## Usage:
- Dockerization is not finished yet, since backend is WIP.

### Manual setup
0. Install Anaconda or Miniconda
1. Create Conda environment based on Python 3.10 (e.g. `conda create -y -k --prefix venv python=3.10`)
2. Activate the Conda environment (e.g. `conda activate venv/`)
3. Download, build and install the appropriate cuda-enabled pytorch packages (e.g. `conda install -y -k pytorch[version=2,build=py3.10_cuda11.7*] torchvision torchaudio pytorch-cuda=11.7 cuda-toolkit ninja git -c pytorch -c nvidia/label/cuda-11.7.0 -c nvidia`)
4. Install the pip requirements (`pip install -r requirements.txt`)
5. start the backend (e.g. `python run_backend.py`) - the FastAPI-Backend, via which LLM and vectorstore functinality is accessed. The backend can already be accessed via the logged uvicorn URL + /docs (Swagger UI)
