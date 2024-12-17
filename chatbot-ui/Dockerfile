FROM node:22.12.0

RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g pnpm

COPY . /app
WORKDIR /app

RUN pnpm install

EXPOSE 3000

CMD ["pnpm", "dev"]

