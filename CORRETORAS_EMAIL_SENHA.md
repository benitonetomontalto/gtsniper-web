# 📊 CORRETORAS COM LOGIN EMAIL + SENHA

Pesquisa completa de APIs de corretoras de opções binárias que suportam autenticação com **email e senha** do usuário.

---

## ✅ SUPORTAM EMAIL + SENHA

### 1. **IQ Option** ✅ (JÁ IMPLEMENTADO)

**Status:** ✅ Funcionando no GTSniper

**Biblioteca:** `iqoptionapi` (não-oficial, mantida pela comunidade)

**Autenticação:**
```python
from iqoptionapi.stable_api import IQ_Option

api = IQ_Option("email@example.com", "senha")
status, reason = api.connect()
```

**Características:**
- ✅ Login direto com email + senha
- ✅ Suporte a 2FA (SMS)
- ✅ Contas PRACTICE e REAL
- ✅ WebSocket para dados em tempo real
- ⚠️ Não-oficial (comunidade)

**Fontes:**
- [GitHub - iqoptionapi/iqoptionapi](https://github.com/iqoptionapi/iqoptionapi)
- [IQ Option API Documentation](https://lu-yi-hsun.github.io/iqoptionapi_pro/)
- [PyPI - iqoptionapi-simple](https://pypi.org/project/iqoptionapi-simple/)

---

### 2. **Quotex** ✅ (RECOMENDADO)

**Status:** ⏳ Pode ser implementado

**Biblioteca:** `pyquotex` ou `quotexapi`

**Autenticação:**
```python
from quotexapi import Quotex

client = Quotex(email="email@example.com", password="senha", lang="pt")
client.connect()
```

**OU com SSID helper:**
```python
from quotexapi import get_ssid

ssid_info = get_ssid(email="email@example.com", password="senha")
api = Quotex(ssid=ssid_info['ssid'])
```

**Características:**
- ✅ Login com email + senha
- ✅ Biblioteca Python disponível
- ✅ Documentação completa
- ⚠️ Não tem API oficial (apenas não-oficial)
- ⚠️ Viola termos de serviço

**Fontes:**
- [GitHub - cleitonleonel/pyquotex](https://github.com/cleitonleonel/pyquotex)
- [GitHub - ericpedra/quotexapi](https://github.com/ericpedra/quotexapi)
- [PyQuotex Documentation](https://cleitonleonel.github.io/pyquotex/)
- [quotexapi document](https://lu-yi-hsun.github.io/quotexapi/)

---

### 3. **Binomo** ✅ (RECOMENDADO)

**Status:** ⏳ Pode ser implementado

**Biblioteca:** `BinomoAPI` (ChipaDevTeam)

**Autenticação:**
```python
import asyncio
from BinomoAPI import BinomoAPI

async def main():
    # Login com email + senha
    login_response = BinomoAPI.login("email@example.com", "senha")

    # Usar API com autenticação
    async with BinomoAPI(
        auth_token=login_response.authtoken,
        device_id=login_response.user_id,
        demo=True
    ) as api:
        balance = await api.get_balance()
        print(f"Saldo: ${balance.amount}")

asyncio.run(main())
```

**Características:**
- ✅ Login com email + senha
- ✅ Biblioteca profissional com async/await
- ✅ Type hints completos
- ✅ WebSocket em tempo real
- ✅ Documentação excelente
- ⚠️ Não-oficial

**Fontes:**
- [BinomoAPI Documentation](https://chipadevteam.github.io/BinomoAPI/)
- [API Reference](https://chipadevteam.github.io/BinomoAPI/api-reference.html)
- [Getting Started Guide](https://chipadevteam.github.io/BinomoAPI/getting-started.html)
- [GitHub - hert0t/Binomo-API](https://github.com/hert0t/Binomo-API)

---

## ❌ NÃO SUPORTAM EMAIL + SENHA

### 4. **Pocket Option** ❌

**Status:** ❌ Apenas SSID

**Problema:**
- Usa Google reCAPTCHA
- Não permite login automatizado
- Requer extração de SSID do navegador

**Autenticação:**
```python
from pocketoptionapi import PocketOption

# Apenas SSID (extraído do navegador)
client = PocketOption(ssid="SESSION_ID_DO_COOKIE")
client.connect()
```

**Por que não funciona:**
- ❌ Google reCAPTCHA bloqueia automação
- ❌ Impossível fazer login programático
- ❌ SSID expira em poucas horas
- ❌ Usuário precisa renovar manualmente

**Fontes:**
- [GitHub - ChipaDevTeam/PocketOptionAPI](https://github.com/ChipaDevTeam/PocketOptionAPI)
- [API Reference](https://chipadevteam.github.io/PocketOptionAPI/api.html)
- [PocketOptionAPI Documentation](https://lu-yi-hsun.github.io/pocketoptionapi/)

---

### 5. **Deriv** ❌

**Status:** ❌ Apenas API Token

**Problema:**
- API oficial, mas NÃO aceita email/senha
- Requer API Token gerado no dashboard
- OAuth para apps de terceiros

**Autenticação:**
```python
from deriv_api import DerivAPI

# Apenas API Token (não email/senha)
api = DerivAPI(app_id=12345, api_token="TOKEN_GERADO")
```

**Por que não funciona:**
- ❌ Sem suporte a email/senha
- ❌ Requer token do dashboard
- ✅ Mais seguro (OAuth)
- ✅ API oficial

**Fontes:**
- [python-deriv-api - PyPI](https://pypi.org/project/python-deriv-api/)
- [Deriv API Documentation](https://deriv-com.github.io/python-deriv-api/)
- [Deriv API - Authentication](https://developers.deriv.com/docs/authentication)
- [Deriv API Dashboard](https://api.deriv.com/dashboard/)

---

## 📊 COMPARAÇÃO

| Corretora | Email+Senha | Biblioteca | Qualidade | Status | Recomendação |
|-----------|-------------|------------|-----------|--------|--------------|
| **IQ Option** | ✅ | iqoptionapi | ⭐⭐⭐⭐ | ✅ Implementado | ✅ Manter |
| **Quotex** | ✅ | pyquotex | ⭐⭐⭐ | ⏳ Não implementado | ✅ Adicionar |
| **Binomo** | ✅ | BinomoAPI | ⭐⭐⭐⭐⭐ | ⏳ Não implementado | ✅ Adicionar |
| **Pocket Option** | ❌ | PocketOptionAPI | ⭐⭐⭐ | ✅ Implementado | ❌ Remover |
| **Deriv** | ❌ | python-deriv-api | ⭐⭐⭐⭐⭐ | ⏳ Não implementado | ⚠️ API Token apenas |

---

## 🎯 RECOMENDAÇÕES

### **Curto Prazo:**

1. ✅ **Manter IQ Option** (já funciona perfeitamente)
2. ❌ **Remover Pocket Option** (SSID é inconveniente)
3. ✅ **Adicionar Quotex** (email+senha, popular no Brasil)
4. ✅ **Adicionar Binomo** (melhor API, async, documentação excelente)

### **Médio Prazo:**

5. ⚠️ **Considerar Deriv** (API oficial, mas requer token)

---

## 🚀 PLANO DE AÇÃO

### **Fase 1: Remover Pocket Option**
- ❌ Remover `pocketoption_broker.py`
- ❌ Remover campos SSID do frontend
- ✅ Manter apenas IQ Option

### **Fase 2: Adicionar Quotex**
- ✅ Implementar `quotex_broker.py`
- ✅ Login com email + senha
- ✅ Testar candles e orders
- ✅ Adicionar ao frontend

### **Fase 3: Adicionar Binomo**
- ✅ Implementar `binomo_broker.py`
- ✅ Async/await nativo
- ✅ Login com email + senha
- ✅ Adicionar ao frontend

### **Resultado Final:**
```
🏦 Selecione a Corretora
┌─────────────────────────────────┐
│ IQ Option                    ▼ │
│ Quotex                          │
│ Binomo                          │
└─────────────────────────────────┘

📧 Email
[email@example.com              ]

🔒 Senha
[••••••••••••                   ]

💰 Tipo de Conta
[PRACTICE ▼]
```

**Todas usando EMAIL + SENHA!** 🎉

---

## ⚠️ AVISOS IMPORTANTES

1. **APIs Não-Oficiais:**
   - IQ Option, Quotex, Binomo: bibliotecas da comunidade
   - Violam termos de serviço das corretoras
   - Risco de bloqueio de conta
   - Usar por sua conta e risco

2. **Segurança:**
   - Nunca compartilhe credenciais
   - Use contas demo para testes
   - Cuidado com bibliotecas maliciosas
   - Sempre verifique código fonte

3. **Legalidade:**
   - Opções binárias podem ser ilegais no seu país
   - Verifique regulamentação local
   - Apenas para fins educacionais

---

**Criado em:** 2025-12-05
**Atualizado em:** 2025-12-05
**Próximo passo:** Decidir quais corretoras implementar
