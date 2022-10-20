FROM python:3.10
ADD WorkshopMonitor.py /
COPY ./data/config.json ./data/config.json 
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python","-u","WorkshopMonitor.py" ]
