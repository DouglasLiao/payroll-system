FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Change ownership to the built-in node user
RUN chown -R node:node /app

# Switch to non-root user
USER node

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
