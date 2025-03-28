FROM python:3.10-alpine

WORKDIR /oceanprotocol_job_details

# Copy the job_details code (with the same depth)
COPY oceanprotocol_job_details /oceanprotocol_job_details/oceanprotocol_job_details
COPY tests /oceanprotocol_job_details/tests
COPY requirements.txt /oceanprotocol_job_details/requirements.txt
COPY requirements-dev.txt /oceanprotocol_job_details/requirements-dev.txt
COPY pyproject.toml /oceanprotocol_job_details/pyproject.toml

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r /oceanprotocol_job_details/requirements.txt && \
    pip install --no-cache-dir -r /oceanprotocol_job_details/requirements-dev.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Check if running dev & tests
CMD ["pytest"]