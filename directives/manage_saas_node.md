# manage_saas_node.md

## Goal

Operar o nó de desenvolvimento Full Stack (CasaOS), mantendo a estabilidade da infraestrutura e executando o fluxo de deploy de novas aplicações via Coolify + Nginx Proxy Manager.

## Infrastructure Map (Production Ready)

Host IP: `192.168.31.88`

| Serviço                 | Porta Host  | URL Interna                  | URL Externa (Via Cloudflare) | Função                    |
| :---------------------- | :---------- | :--------------------------- | :--------------------------- | :------------------------ |
| **Nginx Proxy Manager** | `80`, `443` | `http://192.168.31.88:80`    | (Entrada de todo tráfego)    | Gateway Reverso & SSL     |
| **NPM Admin**           | `81`        | `http://192.168.31.88:81`    | `npm.seudominio.com`         | Gestão de Domínios        |
| **Coolify (PaaS)**      | `8000`      | `http://192.168.31.88:8000`  | `deploy.seudominio.com`      | CI/CD & Automação         |
| **Cloudflared**         | `14333`     | `http://192.168.31.88:14333` | -                            | Túnel Seguro (Zero Trust) |
| **AdGuard Home**        | `3001`      | `http://192.168.31.88:3001`  | -                            | DNS Sinkhole Local        |
| **CasaOS Dashboard**    | `89`        | `http://192.168.31.88:89`    | -                            | Gestão do Servidor        |

## Standard Operating Procedures (SOPs)

### 1. Deploy Workflow (Novo Projeto)

Para colocar uma aplicação (Django/React/Go) no ar:

1.  **Coolify (Build):**
    - Conectar repositório GitHub.
    - Definir comando de build/start.
    - **Porta:** Identificar a porta interna que o Coolify gerou para o app (ex: `3005`).
2.  **Nginx Proxy Manager (Expose):**
    - Criar novo _Proxy Host_.
    - **Domain:** `nome-do-projeto.seudominio.com`.
    - **Forward Host:** `192.168.31.88` (IP do CasaOS).
    - **Forward Port:** Porta do Coolify (ex: `3005`).
    - **SSL:** Request a new SSL Certificate (Let's Encrypt) + Force SSL.
3.  **Cloudflare (Route):**
    - Se o túnel estiver configurado como Wildcard (`*.seudominio.com` -> `192.168.31.88:80`), nenhuma ação é necessária na Cloudflare. O NPM resolve localmente.

### 2. Maintenance & Health Checks

- **Monitoramento:** Verificar `docker ps` semanalmente.
- **Backups:** O Coolify faz backup automático dos bancos de dados configurados nele.
- **Updates:** Usar o Watchtower (se instalado) ou atualizar containers via CasaOS UI.

## Troubleshooting

- **Erro 502 Bad Gateway:** O Nginx Proxy Manager está recebendo a requisição, mas o container de destino (Coolify App) está fora do ar ou na porta errada.
- **Coolify Unhealthy:** Verificar conexão com Postgres (`big-bear-coolify-postgres`). Reiniciar stack se necessário.
- **Túnel Caiu:** Verificar container `cloudflared`. Se necessário, reautenticar via Web UI (`:14333`).

## Automation Tools

A suite de scripts em `execution/` automatiza operações comuns:

### SSH Manager

**Script:** `execution/ssh_manager.py`

Gerencia conexões SSH seguras para executar comandos remotos.

```bash
# Testar conexão
python3 execution/ssh_manager.py

# Executar comando remoto
python3 execution/ssh_manager.py --command "docker ps"

# Executar múltiplos comandos
python3 execution/ssh_manager.py --commands-file commands.txt
```

### Health Check

**Script:** `execution/health_check.py`

Monitora todos os serviços da infraestrutura.

```bash
# Verificação rápida
python3 execution/health_check.py

# Salvar relatório
python3 execution/health_check.py --output ./reports/health_$(date +%Y%m%d).txt

# Formato JSON para integração
python3 execution/health_check.py --format json --alert-on-critical
```

### Deploy App

**Script:** `execution/deploy_app.py`

Orquestra o fluxo completo de deployment de novas aplicações.

```bash
# Modo interativo
python3 execution/deploy_app.py --interactive

# Modo direto
python3 execution/deploy_app.py \
  --app-name myapp \
  --repo https://github.com/user/myapp \
  --port 3005 \
  --domain myapp.example.com
```

### Nginx Config Generator

**Script:** `execution/nginx_config_generator.py`

Gera configurações para NPM Proxy Hosts.

```bash
# Gerar configuração
python3 execution/nginx_config_generator.py \
  --domain myapp.example.com \
  --forward-port 3005 \
  --websockets

# Salvar em arquivo
python3 execution/nginx_config_generator.py \
  --domain myapp.example.com \
  --forward-port 3005 \
  --output config.txt
```

## Workflows

Workflows guiados em `.agent/workflows/`:

- **`/deploy-new-app`** - Deploy completo de nova aplicação
- **`/health-check`** - Verificação semanal de saúde do sistema
- **`/troubleshooting`** - Resolução de problemas comuns

## Configuration

1. Copiar template de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Configurar credenciais SSH no `.env`:

   ```bash
   SAAS_NODE_HOST=192.168.31.88
   SAAS_NODE_SSH_USER=seu_usuario
   SAAS_NODE_SSH_KEY_PATH=/path/to/private/key
   ```

3. Instalar dependências Python:
   ```bash
   cd execution/
   pip install -r requirements.txt
   ```
