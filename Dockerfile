FROM dataloopai/dtlpy-agent:cpu.py3.10.opencv

# Install google-cloud-storage
RUN pip install google-cloud-storage