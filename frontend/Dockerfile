# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Скопировать package.json и package-lock.json (или yarn.lock), поставить зависимости
COPY package*.json ./
RUN npm ci

# Скопировать весь исходник
COPY . .

# Открываем порт Vite (3000 по умолчанию)
EXPOSE 3000

# Запускаем Vite в режиме разработки, принимаем запросы извне
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
