FROM python:3.13

# Create a non-root user for safety
RUN useradd --create-home appuser

WORKDIR /app

# Install build deps and runtime deps from requirements
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy app source
COPY ./app /app/app
COPY ./scripts /app/scripts

# Expose typical uvicorn port
EXPOSE 8000

# Run uvicorn
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
