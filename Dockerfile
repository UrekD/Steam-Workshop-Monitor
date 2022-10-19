FROM python:3.10.7
ADD WorkshopMonitor.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python","-u","WorkshopMonitor.py" ]
