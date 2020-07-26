FROM node:alpine AS builder
WORKDIR /build
COPY frontend ./frontend
COPY package.json ./
COPY webpack.config.js ./
RUN npm install
RUN npm run build_js
RUN npm run build_scss

FROM python:3
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=builder build/static/css/main.css ./static/css/main.css
COPY --from=builder build/static/js/main.js ./static/js/main.js
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

