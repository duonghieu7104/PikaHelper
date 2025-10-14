FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Install only production dependencies for runtime
RUN npm install --only=production && npm cache clean --force

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
