**Final response to user:**

Compreendo. Você está procurando um guia passo a passo com comandos para o Copilot para iniciar a construção de um sistema de gestão de dados de prestadores de serviço, usando Django para o backend (CRUD simples) e React para o frontend (com dashboard, tema claro/escuro, e painéis admin/colaborador).

Aqui está a estrutura do arquivo `PROJETO_SERVICOS.md` com um guia passo a passo e comandos sugeridos para o Copilot.

-----

# PROJETO: Sistema de Gestão de Prestadores de Serviço

## 1\. Configuração Inicial do Projeto

O projeto será dividido em duas pastas principais: `backend` (Django) e `frontend` (React).

### 1.1. Estrutura de Pastas

``` 
/projeto_servicos
├── backend/ (Django)
└── frontend/ (React)

```

### 1.2. Inicialização do Backend (Django)

**No terminal, na pasta `backend/`:**

| Comando no Terminal                      | Comando para o Copilot (Sugestão)                                                                                                                                                                 |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pip install django djangorestframework` | `gera o comando para criar um projeto django chamado 'core' e um app chamado 'api'`                                                                                                               |
| `django-admin startproject core .`       | (Se o projeto ainda não foi criado)                                                                                                                                                               |
| `python manage.py startapp api`          | (Se o app ainda não foi criado)                                                                                                                                                                   |
| Configure `settings.py`                  | `no settings.py, configura o django para usar djangorestframework e o app 'api'`                                                                                                                  |
| Crie um modelo de dados                  | `no arquivo models.py do app 'api', crie um modelo 'Prestador' com os campos: nome (char), funcao (char), salario_base (decimal), total (decimal), e chave_pix (char). Adicione o método __str__` |
| Crie as migrações                        | `gera o comando para criar as migrações no django`                                                                                                                                                |
| Crie um superusuário                     | `gera o comando para criar um superusuário no django`                                                                                                                                             |

**Comandos Adicionais para a API (views.py, urls.py, serializers.py):**

| Comando para o Copilot (Sugestão)                                                           | Ação                                                              |
| :------------------------------------------------------------------------------------------ | :---------------------------------------------------------------- |
| `no arquivo serializers.py, cria um ModelSerializer simples para o modelo 'Prestador'`      | Cria a estrutura para serializar/desserializar dados.             |
| `no arquivo views.py, cria uma ViewSet para o modelo 'Prestador' usando ModelViewSet`       | Implementa a lógica de CRUD.                                      |
| `no arquivo urls.py do app 'api', configura um DefaultRouter para a ViewSet de 'Prestador'` | Define as rotas da API (list, retrieve, create, update, destroy). |

### 1.3. Inicialização do Frontend (React)

**No terminal, na pasta `frontend/`:**

| Comando no Terminal                                    | Comando para o Copilot (Sugestão)                                                                             |
| :----------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ |
| `npx create-react-app .`                               | (Se o app React ainda não foi criado)                                                                         |
| `npm install react-router-dom axios styled-components` | `gera o comando para instalar as dependências: react-router-dom, axios, e styled-components para estilização` |

## 2\. Desenvolvimento do Frontend (React)

O frontend usará React e `styled-components` (ou outra biblioteca de sua preferência) para a estilização e a lógica de tema.

### 2.1. Configuração de Tema (Claro/Escuro)

**No arquivo principal (`App.js` ou Contexto):**

| Comando para o Copilot (Sugestão)                                                                                                | Ação                                                     |
| :------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------- |
| `cria um React Context chamado 'ThemeContext' que armazena o tema atual ('claro' ou 'escuro') e uma função para alternar o tema` | Permite que qualquer componente acesse e alterne o tema. |
| `em App.js, usa o ThemeContext.Provider para envolver a aplicação e aplica estilos globais baseados no tema`                     | Configura o tema para toda a aplicação.                  |

### 2.2. Componentes Principais e Roteamento

**No arquivo principal (`App.js`):**

| Comando para o Copilot (Sugestão)                                                                                                                                     | Ação                           |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------- |
| `em App.js, configura o roteamento com react-router-dom para as seguintes rotas: / (Dashboard), /admin (Painel Admin), /colaborador/:id (Painel Colaborador), /login` | Define a navegação do sistema. |

**Componentes:**

| Comando para o Copilot (Sugestão)                                                                                                     | Ação                                                         |
| :------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------- |
| `cria um componente React chamado 'Dashboard' que busca dados da API /api/prestadores/ e os exibe em uma tabela simples`              | Tela principal de visualização.                              |
| `cria um componente React chamado 'AdminPanel' que permite a criação, edição e exclusão (CRUD) de prestadores`                        | Interface para gestão completa dos dados.                    |
| `cria um componente React chamado 'EmployeePanel' que busca e exibe apenas os dados de um prestador específico com base no ID da URL` | Interface para o colaborador visualizar seus próprios dados. |
| `cria um componente React chamado 'Login' com campos de usuário e senha`                                                              | Implementa a autenticação (simples, inicialmente).           |

## 3\. Implementação de Funcionalidades Específicas

### 3.1. CRUD e Inserção de Dados

| Comando para o Copilot (Sugestão)                                                                                                                      | Ação                                          |
| :----------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------- |
| `no componente 'AdminPanel', cria um formulário React para adicionar um novo prestador, usando axios para enviar um POST request para a API do Django` | Funcionalidade principal de entrada de dados. |
| `cria uma função de edição no 'AdminPanel' que envia um PUT request para a API do Django`                                                              | Funcionalidade de atualização.                |

### 3.2. Dashboard e Visualização de Dados

| Comando para o Copilot (Sugestão)                                                                                                                   | Ação                        |
| :-------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------- |
| `no componente 'Dashboard', implementa o cálculo do salário total de todos os prestadores e exibe esse valor em um card de destaque`                | Agregação de dados simples. |
| `no componente 'Dashboard', usa uma biblioteca de gráficos (como rechart) para criar um gráfico de barras que mostra o 'salario_base' por 'funcao'` | Visualização de dados.      |

### 3.3. Geração de Planilhas

| Comando para o Copilot (Sugestão)                                                                                                                | Ação                                                                                                                    |
| :----------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| `na API do Django, cria uma nova view que recebe um GET request, consulta todos os prestadores e retorna um arquivo Excel (.xlsx) para download` | Implementa a funcionalidade de "gerar planilhas" no backend. (Requer biblioteca como `pandas` ou `openpyxl` no Django). |
| `no componente 'AdminPanel', cria um botão "Exportar para Planilha" que chama o endpoint de exportação do Django`                                | Interface para o usuário baixar a planilha.                                                                             |

## 4\. Próximos Passos (Refinamento)

  * **Autenticação JWT:** Substituir a autenticação simples por JSON Web Tokens (JWT) para proteger a API REST.
  * **Permissões:** Implementar permissões no Django para garantir que apenas administradores acessem o `AdminPanel` e colaboradores apenas o `EmployeePanel` (com seus respectivos dados).
  * **Filtros e Busca:** Adicionar campos de busca e filtros na tabela do `Dashboard` e do `AdminPanel`.
