FROM node:18

WORKDIR /app

COPY . /app
RUN npm install
RUN npm run build

# Install serve to serve the built app
RUN npm install -g serve

EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"] 