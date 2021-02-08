FROM python:3.8

# ====== #
# System #
# ====== #
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y apt-utils

# =========== #
# Python Libs #
COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r requirements.txt

# ---------------------- #
# Install Chrome Browser #
# ---------------------- #
RUN apt-get install -y google-chrome-stable

# --------------------- #
# Install Chrome Driver #
# --------------------- #
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99

# ========== #
# Copy Files #
# ========== #
COPY app/utils/chromedriver .
WORKDIR /app

# Flask Stuff
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "${PYTHONPATH}:/app:/"
ENV FLASK_APP=webservices.py
EXPOSE 5000
COPY ./app .

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
