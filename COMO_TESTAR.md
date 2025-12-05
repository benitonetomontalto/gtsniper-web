# 🧪 COMO TESTAR - Multi-Broker Support

## 🚀 Início Rápido

### 1️⃣ Iniciar Servidor

```bash
cd GTSniper_WEB
python main.py
```

**Aguardar mensagem:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### 2️⃣ Abrir no Navegador

```
http://127.0.0.1:8000
```

---

### 3️⃣ Verificar Patch Carregou

1. **Abrir DevTools (F12)**
2. **Ir na aba "Console"**
3. **Procurar mensagens:**

```
[BROKER PATCH] Inicializando patch de seleção de broker...
[BROKER PATCH] DOM carregado, procurando formulário de login...
[BROKER PATCH] Formulário de login encontrado!
[BROKER PATCH] Injetando seletor de broker...
[BROKER PATCH] Seletor de broker injetado com sucesso! ✅
```

✅ **Se viu essas mensagens:** Patch funcionou!
❌ **Se não viu:** Verificar se `broker-selector-patch.js` está carregando

---

## 🧪 Teste 1: Verificar Seletor Apareceu

### O que verificar:

1. **Tela de login deve ter dropdown ANTES dos campos:**

```
🏦 Selecione a Corretora
┌────────────────────────────────┐
│ IQ Option (Email + Senha)  ▼ │
└────────────────────────────────┘
```

2. **Por padrão deve mostrar campos IQ Option:**
   - Email IQ Option
   - Senha IQ Option
   - Tipo de Conta

✅ **Passou:** Seletor apareceu
❌ **Falhou:** Verificar console (F12) para erros

---

## 🧪 Teste 2: Trocar para Pocket Option

### Passos:

1. **Clicar no dropdown**
2. **Selecionar "Pocket Option (SSID)"**

### O que deve acontecer:

- ❌ Campos IQ Option **somem**:
  - Email IQ Option
  - Senha IQ Option
  - Tipo de Conta (IQ Option)

- ✅ Campos Pocket Option **aparecem**:
  - 🔑 SSID da Pocket Option
  - Botão "❓ Como obter SSID?"
  - Tipo de Conta (Pocket Option)

✅ **Passou:** Campos trocaram
❌ **Falhou:** Verificar console para erros

---

## 🧪 Teste 3: Ver Instruções SSID

### Passos:

1. **Selecionar "Pocket Option"**
2. **Clicar no botão "❓ Como obter SSID?"**

### O que deve acontecer:

- Modal abre com instruções:
  ```
  🔑 Como obter SSID da Pocket Option

  1. Abra https://pocketoption.com no navegador
  2. Faça login normalmente
  3. Pressione F12 para abrir DevTools
  ...
  ```

- **Botão "Entendi"** fecha o modal

✅ **Passou:** Modal funcionou
❌ **Falhou:** Verificar console

---

## 🧪 Teste 4: Login com IQ Option

### Pré-requisitos:
- ✅ Credenciais válidas da IQ Option
- ✅ Token de ativação válido

### Passos:

1. **Ativar licença** (se ainda não ativou)
2. **Garantir que "IQ Option" está selecionado**
3. **Preencher:**
   - Email IQ Option: `seu-email@iqoption.com`
   - Senha IQ Option: `sua-senha`
   - Tipo de Conta: `PRACTICE` ou `REAL`
4. **Clicar "Conectar e Entrar"**

### O que verificar no Console:

```
[BROKER PATCH] Formulário submetido, processando...
[BROKER PATCH] Dados de login: {username: "user", broker_type: "iqoption", ...}
[BROKER PATCH] Resposta do login: {broker_connected: true, broker_type: "iqoption", ...}
[BROKER PATCH] ✅ Conectado ao iqoption
```

### O que deve acontecer:

- ✅ Login bem-sucedido
- ✅ Redireciona para dashboard
- ✅ Mostra saldo da conta
- ✅ Sistema funciona normalmente

✅ **Passou:** IQ Option funcionando
❌ **Falhou:** Ver mensagem de erro

---

## 🧪 Teste 5: Login com Pocket Option

### Pré-requisitos:
- ✅ Conta na Pocket Option
- ✅ SSID válido (ver instruções abaixo)
- ✅ Token de ativação válido

### Como obter SSID:

1. **Abrir https://pocketoption.com**
2. **Fazer login**
3. **F12 → Application → Cookies → https://pocketoption.com**
4. **Procurar cookie "ssid"**
5. **Copiar o VALOR** (string longa tipo: `abc123xyz...`)

### Passos:

1. **Ativar licença** (se ainda não ativou)
2. **Selecionar "Pocket Option" no dropdown**
3. **Preencher:**
   - SSID: `[VALOR_COPIADO_DO_COOKIE]`
   - Tipo de Conta: `PRACTICE` ou `REAL`
4. **Clicar "Conectar e Entrar"**

### O que verificar no Console:

```
[BROKER PATCH] Formulário submetido, processando...
[BROKER PATCH] Dados de login: {username: "user", broker_type: "pocketoption", ...}
[BROKER PATCH] Resposta do login: {broker_connected: true, broker_type: "pocketoption", ...}
[BROKER PATCH] ✅ Conectado ao pocketoption
```

### O que deve acontecer:

- ✅ Login bem-sucedido
- ✅ Redireciona para dashboard
- ✅ Mostra saldo da conta
- ✅ Sistema funciona normalmente

✅ **Passou:** Pocket Option funcionando
❌ **Falhou:** Ver mensagem de erro

---

## 🧪 Teste 6: Verificar Backend

### Testar endpoint de brokers disponíveis:

```bash
curl http://127.0.0.1:8000/api/brokers/available
```

**Resposta esperada:**
```json
{
  "brokers": [
    {
      "broker_type": "iqoption",
      "name": "IQ Option",
      "available": true,
      "auth_type": "email_password",
      "description": "Conecta via email e senha..."
    },
    {
      "broker_type": "pocketoption",
      "name": "Pocket Option",
      "available": true,
      "auth_type": "ssid",
      "description": "Conecta via SSID..."
    }
  ]
}
```

✅ **Passou:** Ambos brokers disponíveis
⚠️ **Pocket Option `available: false`:** Biblioteca não instalada
   - Instalar: `pip install git+https://github.com/ChipaDevTeam/PocketOptionAPI.git`

---

## 🐛 Troubleshooting

### ❌ Patch não carregou

**Verificar:**
```javascript
// No console
document.getElementById('broker-selector-container')
// Se retornar null → patch não injetou
```

**Soluções:**
1. Limpar cache do navegador (Ctrl+Shift+R)
2. Verificar se `broker-selector-patch.js` existe em `frontend_dist/assets/`
3. Verificar se `index.html` tem `<script src="/assets/broker-selector-patch.js"></script>`

---

### ❌ Campos não trocam ao selecionar broker

**Verificar no console:**
```
[BROKER PATCH] Broker selecionado: pocketoption
```

Se não apareceu → event listener não funcionou

**Solução:** Recarregar página (F5)

---

### ❌ Login falha com "Pocket Option não disponível"

**Causa:** Biblioteca `pocketoptionapi` não instalada

**Solução:**
```bash
pip install git+https://github.com/ChipaDevTeam/PocketOptionAPI.git
```

Depois **reiniciar servidor**:
```bash
python main.py
```

---

### ❌ Login falha com "SSID inválido"

**Causas possíveis:**
1. SSID expirado (validade: algumas horas)
2. SSID copiado incorretamente
3. SSID não é da conta correta

**Solução:**
1. Obter novo SSID:
   - F12 → Application → Cookies → ssid
   - Copiar VALOR completo (sem espaços)
2. Colar no campo SSID
3. Tentar novamente

---

### ❌ "Formulário de login não encontrado após 10 segundos"

**Causa:** HTML do frontend mudou

**Solução:**
1. Verificar se página realmente carregou
2. Ver estrutura do HTML no DevTools
3. Pode precisar ajustar seletores em `broker-selector-patch.js`

---

## 📊 Checklist Completo

### Frontend
- [ ] Patch carregou (ver console)
- [ ] Seletor de broker apareceu
- [ ] Dropdown tem IQ Option e Pocket Option
- [ ] IQ Option selecionado por padrão
- [ ] Campos IQ Option visíveis
- [ ] Trocar para Pocket Option → campos mudam
- [ ] Botão "Como obter SSID?" funciona
- [ ] Modal abre e fecha corretamente

### Backend
- [ ] Servidor rodando (porta 8000)
- [ ] Endpoint `/api/brokers/available` retorna brokers
- [ ] IQ Option disponível
- [ ] Pocket Option disponível (ou mostra como instalar)

### Login IQ Option
- [ ] Login com credenciais válidas funciona
- [ ] Redireciona para dashboard
- [ ] Mostra saldo
- [ ] Scanner funciona

### Login Pocket Option
- [ ] SSID válido obtido
- [ ] Login com SSID funciona
- [ ] Redireciona para dashboard
- [ ] Mostra saldo
- [ ] Scanner funciona

### Compatibilidade
- [ ] Frontend antigo ainda funciona (sem selecionar broker)
- [ ] IQ Option retrocompatível
- [ ] LocalStorage armazena broker_type

---

## ✅ Pronto para Deploy?

**Sim, se:**
- ✅ Todos testes passaram
- ✅ IQ Option funcionando
- ✅ Pocket Option funcionando (se biblioteca instalada)
- ✅ Scanner funcionando com ambos brokers

**Aguardar, se:**
- ❌ Algum teste falhou
- ❌ Erros no console
- ❌ Login não funciona

---

## 🚀 Deploy no Render

Quando todos testes passarem localmente:

1. **Push para GitHub:**
   ```bash
   git push origin main
   ```

2. **Render detectará mudanças e fará deploy automático**

3. **Aguardar deploy concluir**

4. **Testar novamente na URL do Render**

---

**Criado em:** 2025-12-05
**Status:** Pronto para Testes
**Ambiente:** Local (http://127.0.0.1:8000)
