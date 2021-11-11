FROM python:3.9

RUN mkdir /opt/smb_server

ADD server/ /opt/smb_server

RUN pip install -r /opt/smb_server/requirements.txt

EXPOSE 6969/tcp

WORKDIR /opt/smb_server

ENTRYPOINT [ "python", "main.py" ]