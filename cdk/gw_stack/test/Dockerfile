FROM python:3.7.5-slim-buster
ADD analyzer.py analyzer.py 
RUN pip install flask
ENTRYPOINT ["python", "analyzer.py"]
CMD ["--help"]