FROM python:3.10.7
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD WorkshopMonitor.py /
CMD [ "python","-u","WorkshopMonitor.py" ]
