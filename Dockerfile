FROM rootproject/root-ubuntu16:latest
USER root
RUN curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && \
    python /tmp/get-pip.py && \
    rm /tmp/get-pip.py

RUN apt-get update && apt-get install -y parallel jq
RUN pip install uproot tabulate click pandas matplotlib pyyaml shapely pyhf[minuit]==0.1.2



ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
ENV SHELL bash
RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY . ${HOME}

RUN echo "source /usr/local/bin/thisroot.sh" >> $HOME/.bashrc 
RUN pip install jupyter joblib requests tqdm shapely descartes

USER root
RUN chown -R ${NB_UID} ${HOME}
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

RUN chown ${NB_UID} /entrypoint.sh
RUN chmod +x  /entrypoint.sh

USER ${NB_USER}
WORKDIR ${HOME}
