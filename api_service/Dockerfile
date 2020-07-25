FROM node:alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build_js
RUN npm run build_scss

FROM python:3
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

