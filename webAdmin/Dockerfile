# Frontend Dockerfile
FROM node:25-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy application
COPY . .

# Build app
RUN npm run build

# Expose port
EXPOSE 3000

# Run server
CMD ["npm", "start"]

