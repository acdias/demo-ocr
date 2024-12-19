# Use official Node.js 20 LTS Alpine image
FROM --platform=linux/x86_64 node:20-alpine3.19

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apk add --no-cache bash

# Copy the Quasar app files into the container
COPY . .

# Install Quasar CLI and dependencies
RUN npm install -g @quasar/cli

# Install app dependencies (assuming you have a package.json)
RUN npm install

# Build the Quasar app (for SPA)
RUN quasar build -m spa

# Expose port 80 for the web server
EXPOSE 9000

# Serve the app with Nginx
CMD ["quasar", "serve", "dist/spa", "-p", "9000"]