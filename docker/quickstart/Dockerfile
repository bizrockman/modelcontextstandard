# docker/quickstart/Dockerfile
FROM python:3.11-slim

# Install FastAPI and Uvicorn (plus Pydantic for response model)
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic

WORKDIR /app
# Copy only the demo script (everything else is untouched)
COPY fastapi_server_mcs_quickstart.py .

EXPOSE 8000
CMD ["uvicorn", "fastapi_server_mcs_quickstart:app", "--host", "0.0.0.0", "--port", "8000"]
