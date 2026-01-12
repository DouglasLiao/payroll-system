# Environment Variables Configuration

Este projeto utiliza variáveis de ambiente para configuração, permitindo diferentes configurações para desenvolvimento e produção.

## Configuração Local (Desenvolvimento)

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. O arquivo `.env` já está configurado para desenvolvimento local:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_ENV=development
```

## Configuração de Produção

1. Crie um arquivo `.env.production`:
```bash
cp .env.production.example .env.production
```

2. Atualize com a URL da sua API de produção:
```env
VITE_API_BASE_URL=https://api.seudominio.com/api
VITE_APP_ENV=production
```

## Variáveis Disponíveis

### `VITE_API_BASE_URL`
- **Descrição**: URL base da API backend
- **Desenvolvimento**: `http://localhost:8000/api`
- **Produção**: URL do seu servidor de produção
- **Obrigatório**: Não (fallback para localhost)

### `VITE_APP_ENV`
- **Descrição**: Ambiente da aplicação
- **Valores**: `development` | `production`
- **Obrigatório**: Não

## Build para Produção

Ao fazer build para produção, o Vite automaticamente usará as variáveis do `.env.production`:

```bash
npm run build
```

## Segurança

⚠️ **IMPORTANTE**: 
- Nunca commite arquivos `.env` ou `.env.production` no Git
- Apenas os arquivos `.example` devem ser commitados
- Variáveis com prefixo `VITE_` são expostas no código do cliente
- Não coloque informações sensíveis (senhas, tokens) em variáveis `VITE_*`

## Acesso no Código

```typescript
// Acessar variáveis de ambiente
const apiUrl = import.meta.env.VITE_API_BASE_URL
const env = import.meta.env.VITE_APP_ENV

// Verificar modo
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
```

## Troubleshooting

### Variável não está sendo lida
1. Certifique-se que a variável tem o prefixo `VITE_`
2. Reinicie o servidor de desenvolvimento após alterar `.env`
3. Limpe o cache: `rm -rf node_modules/.vite`

### Build de produção não usa variáveis corretas
1. Verifique se `.env.production` existe
2. Certifique-se que está usando `npm run build` (não `npm run dev`)
