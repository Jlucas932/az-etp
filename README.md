# 🎯 Sistema ETP - Gerador de Estudo Técnico Preliminar

Sistema inteligente para geração de documentos de Estudo Técnico Preliminar (ETP) conforme a Lei 14.133/21.

## 🚀 **Configuração Inicial**

### 1. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 2. **Configurar API Key da OpenAI**

#### **Opção A: Arquivo .env (Recomendado)**
1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` e substitua `sua_api_key_aqui` pela sua chave real:
   ```env
   OPENAI_API_KEY=sk-proj-sua_chave_real_aqui
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

#### **Opção B: Variável de Ambiente**
```bash
export OPENAI_API_KEY=sk-proj-sua_chave_real_aqui
```

### 3. **Obter API Key da OpenAI**
1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em "Create new secret key"
4. Copie a chave gerada (começa com `sk-proj-`)

### 4. **Executar o Sistema**
```bash
python src/main.py
```

### 5. **Acessar a Interface**
- **URL**: http://localhost:5002
- **Interface**: Chat com IA

## 📋 **Funcionalidades**

### **🔹 Gerador de ETP**
- 5 perguntas obrigatórias da Lei 14.133/21
- Fluxo conversacional natural
- Validação automática de respostas
- Geração de documento Word profissional

### **🔹 Chat Especializado**
- Assistente especializado em compras públicas
- Base de conhecimento da Lei 14.133/21
- Respostas formatadas e organizadas
- Suporte a perguntas técnicas

## 🛠️ **Como Usar**

### **📋 Criar Novo ETP**
1. Clique em "Iniciar Novo ETP"
2. Responda as perguntas no chat:
   - Descrição da necessidade
   - Previsão no PCA (Sim/Não)
   - Normas legais aplicáveis
   - Quantitativo e valor estimado
   - Parcelamento da contratação (Sim/Não)
3. Sistema gera preview do documento
4. Download do arquivo Word final

### **💬 Chat sobre Compras Públicas**
1. Clique em "Chat sobre Compras Públicas"
2. Faça perguntas sobre:
   - Modalidades de licitação
   - Procedimentos da Lei 14.133/21
   - Elaboração de documentos
   - Critérios de sustentabilidade

## 🔧 **Estrutura do Projeto**

```
etp_sistema_atualizado/
├── .env.example           # Modelo de configuração
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── src/
│   ├── main.py           # Servidor principal
│   ├── models/           # Modelos de dados
│   ├── routes/           # Rotas da API
│   ├── utils/            # Utilitários
│   └── static/           # Frontend (HTML/CSS/JS)
└── database/             # Banco de dados SQLite
```

## ⚠️ **Solução de Problemas**

### **Erro: "API Key não configurada"**
- Verifique se o arquivo `.env` existe
- Confirme se a API key está correta no arquivo `.env`
- Teste a API key em: https://platform.openai.com/playground

### **Erro: "Unexpected token"**
- Verifique sua conexão com a internet
- Confirme se a API key tem créditos disponíveis
- Teste o endpoint `/health` para verificar a configuração

### **Erro: "Module not found"**
- Execute: `pip install -r requirements.txt`
- Verifique se está no diretório correto

## 📞 **Suporte**

Para dúvidas ou problemas:
1. Verifique se seguiu todas as etapas de configuração
2. Teste o endpoint `/health` para diagnóstico
3. Confirme se a API key da OpenAI está válida

## 🎉 **Versão**
- **Versão**: 2.0.0
- **Compatibilidade**: Lei 14.133/21
- **Tecnologias**: Flask + OpenAI + SQLite