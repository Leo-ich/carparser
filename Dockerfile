# python (Debian)
FROM python:3.11-slim

LABEL "description"="carparser"

# Setup env
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

# Install python and firefox dependencies
COPY requirements.txt ./

RUN useradd --create-home appuser \
    && apt-get update \
#    && apt-get install -y --no-install-recommends \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && playwright install-deps firefox \
    && apt-get clean

# Switch to a new user
USER appuser
WORKDIR /home/appuser/app

# Install playwright firefox
RUN playwright install firefox

# Install application into container
COPY --chown=appuser ./ ./

# Run the application
ENTRYPOINT ["scrapy"]
CMD ["crawl", "avito_car"]
#CMD ["/usr/bin/env", "bash"]