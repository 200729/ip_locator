FROM continuumio/miniconda3:latest

ARG ENV_NAME=ip_locator_env
ARG APP_DIR=app
ARG PORT=8080

RUN conda init

WORKDIR /$APP_DIR

COPY environment.yml /$APP_DIR/environment.yml

RUN conda env create -f environment.yml

RUN echo "conda activate $ENV_NAME" >> ~/.bashrc

ENV PATH=/opt/conda/envs/$ENV_NAME/bin:$PATH

ENV PATH=/$APP_DIR:$PATH

ENV PYTHONPATH=/$APP_DIR

COPY api/ /$APP_DIR/api
COPY infrastructure/ /$APP_DIR/infrastructure
COPY ipstack_client/ /$APP_DIR/ipstack_client
COPY model/ /$APP_DIR/model
COPY utils/ /$APP_DIR/utils
COPY main.py /$APP_DIR/main.py

EXPOSE $PORT

ENTRYPOINT ["fastapi", "run", "main.py", "--port", "8080"]
