FROM quay.io/jupyter/scipy-notebook:latest

USER ${NB_UID}

# Install MLFlow 
RUN pip install --pre --no-cache-dir mlflow && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"