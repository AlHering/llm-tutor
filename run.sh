#!/bin/bash
cd "/project"
printf "\n%s\n" "${delimiter}"
printf "Activating conda environment and entering __main__.py"
printf "\n%s\n" "${delimiter}"
source "${CONDA_DIR}/etc/profile.d/conda.sh" && streamlit run __main__.py --server.port 7860
