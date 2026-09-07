# frontend/Dockerfile
FROM node:16-alpine

# Copy package.json and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the code
COPY . .

# Build the app
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Serve the app
CMD ["npm", "run", "serve"]