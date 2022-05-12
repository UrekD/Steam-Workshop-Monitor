FROM python:3.10
ADD WorkshopMonitor.py /
ADD config.json /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python","-u","WorkshopMonitor.py" ]
