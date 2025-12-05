# FASE 3 - Integração Frontend (Multi-Broker)

## ✅ Backend Concluído

### Arquivos Modificados:

1. **app/models/schemas.py**
   - Adicionado `broker_type` em `LoginRequest`
   - Adicionado campos para Pocket Option: `pocketoption_ssid`, `pocketoption_account_type`
   - Adicionado campos genéricos em `TokenResponse`: `broker_type`, `broker_connected`, `broker_message`, `broker_balance`, `broker_account_type`
   - Mantida compatibilidade retroativa com campos `iq_option_*`
   - Criados modelos `BrokerInfo` e `AvailableBrokersResponse`

2. **app/api/routes.py**
   - Importados `BrokerFactory`, `BaseBroker` e novos schemas
   - Adicionado `_broker_instances` dict para armazenar brokers por usuário
   - Atualizado endpoint `/auth/login` para suportar múltiplos brokers
   - Criado endpoint `/brokers/available` (GET) que lista brokers disponíveis
   - Mantida compatibilidade 100% com IQ Option existente

---

## 📋 Mudanças Necessárias no Frontend

### 1. Tela de Login

#### 1.1. Adicionar Seleção de Broker

**Localização**: Formulário de login (provavelmente `Login.vue`, `Login.tsx` ou similar)

**Implementação**:

```html
<!-- Dropdown para selecionar broker -->
<select v-model="loginForm.broker_type" @change="onBrokerChange">
  <option value="iqoption">IQ Option</option>
  <option value="pocketoption">Pocket Option</option>
</select>
```

**Dados**:
```javascript
data() {
  return {
    loginForm: {
      username: '',
      password: '',
      access_token: '',
      broker_type: 'iqoption', // Default

      // IQ Option
      iqoption_email: '',
      iqoption_password: '',
      iqoption_account_type: 'PRACTICE',

      // Pocket Option
      pocketoption_ssid: '',
      pocketoption_account_type: 'PRACTICE'
    }
  }
}
```

#### 1.2. Campos Condicionais

**IQ Option** (`broker_type === "iqoption"`):
```html
<div v-if="loginForm.broker_type === 'iqoption'">
  <input v-model="loginForm.iqoption_email" placeholder="Email IQ Option" />
  <input v-model="loginForm.iqoption_password" type="password" placeholder="Senha IQ Option" />
  <select v-model="loginForm.iqoption_account_type">
    <option value="PRACTICE">Conta Demo</option>
    <option value="REAL">Conta Real</option>
  </select>
</div>
```

**Pocket Option** (`broker_type === "pocketoption"`):
```html
<div v-if="loginForm.broker_type === 'pocketoption'">
  <input v-model="loginForm.pocketoption_ssid" placeholder="SSID" />
  <select v-model="loginForm.pocketoption_account_type">
    <option value="PRACTICE">Conta Demo</option>
    <option value="REAL">Conta Real</option>
  </select>

  <!-- Link para instruções -->
  <button @click="showSSIDInstructions">Como obter SSID?</button>
</div>
```

#### 1.3. Modal de Instruções SSID

```html
<div v-if="showSSIDModal" class="modal">
  <h3>Como obter SSID da Pocket Option</h3>
  <ol>
    <li>Abra https://pocketoption.com no navegador</li>
    <li>Faça login normalmente</li>
    <li>Pressione F12 para abrir DevTools</li>
    <li>Vá na aba "Application" (Chrome) ou "Storage" (Firefox)</li>
    <li>No menu lateral, expanda "Cookies"</li>
    <li>Clique em "https://pocketoption.com"</li>
    <li>Procure o cookie chamado "ssid"</li>
    <li>Copie o VALOR do cookie (string longa)</li>
    <li>Cole aqui no campo SSID</li>
  </ol>
  <p><strong>IMPORTANTE:</strong></p>
  <ul>
    <li>O SSID expira após algumas horas</li>
    <li>Você precisará renovar quando expirar</li>
    <li>Não compartilhe seu SSID (é como uma senha)</li>
  </ul>
  <button @click="showSSIDModal = false">Fechar</button>
</div>
```

---

### 2. API Request (Login)

#### Request para o Backend:

```javascript
async function login() {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(loginForm)
  });

  const data = await response.json();

  // Verificar conexão do broker
  if (data.broker_connected) {
    console.log(`✅ Conectado ao ${data.broker_type}`);
    console.log(`Saldo: $${data.broker_balance}`);
    console.log(`Tipo de conta: ${data.broker_account_type}`);

    // Armazenar token
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('broker_type', data.broker_type);

    // Redirecionar para dashboard
    router.push('/dashboard');
  } else {
    alert(`Erro ao conectar: ${data.broker_message}`);
  }
}
```

---

### 3. Buscar Brokers Disponíveis (Opcional)

Se quiser carregar brokers dinamicamente:

```javascript
async function loadAvailableBrokers() {
  const response = await fetch('/api/brokers/available');
  const data = await response.json();

  this.availableBrokers = data.brokers.filter(b => b.available);

  // Exibir apenas brokers disponíveis no dropdown
}
```

---

### 4. Exibir Informações do Broker Conectado

No dashboard ou header:

```html
<div class="broker-info">
  <span>{{ brokerName }}</span>
  <span>Saldo: ${{ balance }}</span>
  <span>{{ accountType === 'PRACTICE' ? '💵 Demo' : '💰 Real' }}</span>
</div>
```

```javascript
data() {
  return {
    brokerType: localStorage.getItem('broker_type') || 'iqoption',
    brokerName: 'IQ Option', // ou 'Pocket Option'
    balance: 0,
    accountType: 'PRACTICE'
  }
}
```

---

## 🎯 Fluxo Completo

1. **Usuário abre tela de login**
2. **Seleciona broker** (IQ Option ou Pocket Option)
3. **Campos mudam dinamicamente** baseado na seleção
4. **Preenche credenciais**:
   - IQ Option: email + senha
   - Pocket Option: SSID
5. **Clica em "Login"**
6. **Backend conecta ao broker selecionado**
7. **Frontend recebe resposta**:
   - `broker_connected: true` → Redireciona para dashboard
   - `broker_connected: false` → Mostra erro
8. **Dashboard exibe broker conectado e saldo**

---

## 🔄 Compatibilidade Retroativa

### Campos Mantidos (Deprecated):

- `iq_option_connected`
- `iq_option_message`
- `iq_option_balance`
- `iq_option_account_type`

**Frontend antigo continuará funcionando** sem modificações!

**Frontend novo** deve usar:
- `broker_connected`
- `broker_message`
- `broker_balance`
- `broker_account_type`

---

## 🧪 Teste Manual

### Testar IQ Option:
```json
POST /api/auth/login
{
  "username": "user123",
  "access_token": "GT4-XXX",
  "broker_type": "iqoption",
  "iqoption_email": "test@example.com",
  "iqoption_password": "password",
  "iqoption_account_type": "PRACTICE"
}
```

### Testar Pocket Option:
```json
POST /api/auth/login
{
  "username": "user123",
  "access_token": "GT4-XXX",
  "broker_type": "pocketoption",
  "pocketoption_ssid": "LONG_SSID_STRING_HERE",
  "pocketoption_account_type": "PRACTICE"
}
```

### Listar Brokers:
```
GET /api/brokers/available
```

**Resposta**:
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

---

## ⚠️ IMPORTANTE

1. **NÃO MODIFICAR** arquivos em `frontend_dist/` diretamente (são compilados)
2. **Modificar** apenas arquivos fonte do frontend (`.vue`, `.tsx`, `.jsx`)
3. **Recompilar** frontend após modificações
4. **Testar ambos brokers** antes de deploy

---

## 🚀 Próximos Passos

Após integração frontend:
1. Testar login com IQ Option (deve continuar funcionando)
2. Testar login com Pocket Option (novo)
3. Verificar que scanner funciona com ambos brokers
4. Deploy no Render

---

## 📚 Arquitetura de Referência

```
Frontend                Backend
--------                -------
Login Screen    --->    POST /auth/login
  ↓ broker_type             ↓
  ↓ credentials        BrokerFactory
  ↓                         ↓
  |-----> iqoption     IQOptionBroker (adapter)
  |                         ↓
  |-----> pocketoption PocketOptionBroker
                            ↓
                      BaseBroker (interface comum)
                            ↓
                        Scanner (funciona com ambos)
```

---

**Documentação criada em:** 2025-01-XX
**Status Backend:** ✅ Completo
**Status Frontend:** ⏳ Aguardando implementação
