FROM quay.io/jupyter/base-notebook:x86_64-python-3.11.6

USER ${NB_UID}

# Install MLFlow 
RUN pip install --pre --no-cache-dir mlflow && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"