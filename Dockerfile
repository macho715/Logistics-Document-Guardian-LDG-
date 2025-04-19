# ---- build stage ----
FROM python:3.11-slim AS build

# 1) 시스템 패키지
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-kor \
        libleptonica-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) 가상환경
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# 3) 의존성
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install .[dev]

# ---- runtime stage ----
FROM python:3.11-slim

# Copy Tesseract data
COPY --from=build /usr/share/tesseract-ocr/ /usr/share/tesseract-ocr/

# Copy installed packages
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY src/ ./src

# Make Python output unbuffered (recommended for containers)
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
# ENTRYPOINT ["python", "-m", "cli.main"]
# For now, let's make it easy to run arbitrary commands or explore
CMD ["bash"] 