FROM node:20-alpine

# Cria a pasta e já define o dono como o usuário "node" não-root do alpine
WORKDIR /app
RUN chown node:node /app

# Daqui pra baixo entramos como node para ganhar agilidade, evitando "chown -R"
USER node

# Copia base do workspace (com permissões próprias na transação)
COPY --chown=node:node package.json package-lock.json ./
COPY --chown=node:node payroll-landing-page/package.json ./payroll-landing-page/
COPY --chown=node:node payroll-design-system/package.json ./payroll-design-system/

# Instala rápido como user node
RUN npm install

# Copia os source-codes em fração de segundos
COPY --chown=node:node payroll-landing-page/ ./payroll-landing-page/
COPY --chown=node:node payroll-design-system/ ./payroll-design-system/

EXPOSE 5174

CMD ["npm", "run", "dev", "--workspace=payroll-landing-page", "--", "--host", "0.0.0.0", "--port", "5174"]
