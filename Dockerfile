FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY .env .

RUN pip install --upgrade pip

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uwsgi

COPY . .

EXPOSE 80

CMD ["sh", "-c", "export $(grep -v '^#' /app/.env | xargs) && ./start.sh"]