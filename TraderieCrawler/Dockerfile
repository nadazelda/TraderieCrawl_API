FROM python:3.10-slim

# 시스템 패키지 설치


# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 lsb-release ca-certificates \
    libx11-dev libx11-6 libgbm-dev libasound2 \
    libnss3 libnspr4 libxss1 libxext6 libgtk-3-0 fonts-liberation \
    && apt-get clean

RUN apt-get remove -y chromium-browser


# # Node.js 설치 (LocalTunnel 실행 위해)
# RUN apt-get update && apt-get install -y curl \
#     && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs \
#     && npm install -g localtunnel



# 최신 Chrome 설치
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y \
    && rm google-chrome-stable_current_amd64.deb \
    && echo "Chrome installed"

# ChromeDriver 136 설치
RUN apt-get update && apt-get install -y unzip wget && \
    wget -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.92/linux64/chromedriver-linux64.zip && \
    unzip chromedriver.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver
# ChromeDriver v114 설치
#RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
#    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
#    && chmod +x /usr/bin/chromedriver \
#    && rm /tmp/chromedriver.zip

# 환경 변수 설정
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"


# 작업 디렉토리 및 파일 복사
WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 기본 실행 명령어
#/app/main.py 가 있기때문
CMD ["python", "run.py"] 
