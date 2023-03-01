# python (Debian)
FROM python:3.11-slim

LABEL "description"="carparser"

# Setup env
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install firefox dependencies
RUN useradd --create-home appuser \
    && apt-get update \
#    && apt-get install -y --no-install-recommends \
    && python3 -m pip install --no-cache-dir playwright==1.30 \
    && playwright install-deps firefox \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch to a new user
USER appuser
WORKDIR /home/appuser/app

# Install playwright firefox
RUN playwright install firefox

# Install python dependencies
COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt \
    && mkdir /home/appuser/datadir

# Install application into container
COPY --chown=appuser ./ ./

VOLUME /home/appuser/datadir

# Run the application
#ENTRYPOINT ["scrapy"]
CMD ["scrapy", "crawl", "avito_car"]
#CMD ["/usr/bin/env", "bash"]