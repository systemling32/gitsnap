FROM python:3.12.3-slim-bookworm

WORKDIR /app

RUN apt update && apt upgrade -y && apt install -y  --no-install-recommends firefox-esr borgbackup wget git && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/
RUN touch /repos.txt && git config --global safe.directory '*' && pip install --no-cache-dir -r /app/requirements.txt
ENV PATH="$PATH:/usr/local/bin"
COPY main.py /app/
ENTRYPOINT ["python3","-u","main.py","/storage/","-l","/repos.txt"]
CMD []
