# Use an official Node.js runtime as the base image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install Node.js dependencies, including the 'redis' module
RUN npm install

# Copy the rest of your Node.js application code to the container
COPY . .

# Define the command to start your Node.js application
CMD node program.js
