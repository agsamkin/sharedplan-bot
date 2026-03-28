# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY mini_app/frontend/package.json mini_app/frontend/package-lock.json* ./
RUN npm ci
COPY mini_app/frontend/ ./
RUN npm run build

# Stage 2: Python app
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist /app/mini_app/frontend/dist

CMD ["python", "-m", "app.main"]
