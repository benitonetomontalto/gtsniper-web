# ⚡ QUICK START - Multi-Broker GTSniper

## 🚀 Início Ultra Rápido

### 1. Iniciar

```bash
cd GTSniper_WEB
python main.py
```

### 2. Acessar

```
http://127.0.0.1:8000
```

### 3. Login

**IQ Option:**
1. Selecionar "IQ Option"
2. Email + Senha
3. Tipo de conta
4. Conectar

**Pocket Option:**
1. Selecionar "Pocket Option"
2. Obter SSID:
   - https://pocketoption.com → Login
   - F12 → Application → Cookies → ssid → Copiar
3. Colar SSID
4. Tipo de conta
5. Conectar

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| **[README_MULTI_BROKER.md](README_MULTI_BROKER.md)** | 📖 README principal |
| **[COMO_TESTAR.md](COMO_TESTAR.md)** | 🧪 Guia de testes completo |
| **[PLANO_MULTI_CORRETORAS.md](PLANO_MULTI_CORRETORAS.md)** | 🏗️ Arquitetura detalhada |
| **[PATCH_FRONTEND_APLICADO.md](PATCH_FRONTEND_APLICADO.md)** | 🎨 Como funciona o frontend |
| **[VISUAL_PREVIEW.md](VISUAL_PREVIEW.md)** | 👁️ Preview visual da UI |
| **[RESUMO_MULTI_BROKER.md](RESUMO_MULTI_BROKER.md)** | 📊 Resumo completo |

---

## ✅ Checklist Rápido

### Frontend:
- [ ] Seletor de broker aparece?
- [ ] Campos mudam ao trocar broker?
- [ ] Modal SSID funciona?

### IQ Option:
- [ ] Login funciona?
- [ ] Saldo aparece?
- [ ] Scanner funciona?

### Pocket Option:
- [ ] Login com SSID funciona?
- [ ] Saldo aparece?
- [ ] Scanner funciona?

---

## 🐛 Problemas Comuns

### Patch não carregou
```javascript
// Console (F12)
[BROKER PATCH] Seletor de broker injetado com sucesso! ✅
```
❌ Não apareceu? Limpar cache (Ctrl+Shift+R)

### Pocket Option não disponível
```bash
pip install git+https://github.com/ChipaDevTeam/PocketOptionAPI.git
python main.py
```

### SSID inválido
- Expirou? Obter novo SSID
- Copiou errado? Copiar novamente (F12 → Cookies)

---

## 🚀 Deploy

```bash
git push origin main
# Aguardar Render fazer deploy
```

---

## 📞 Ajuda

- **Testes:** [COMO_TESTAR.md](COMO_TESTAR.md)
- **Troubleshooting:** [COMO_TESTAR.md](COMO_TESTAR.md) seção 🐛
- **Arquitetura:** [PLANO_MULTI_CORRETORAS.md](PLANO_MULTI_CORRETORAS.md)

---

**✅ Pronto! Sistema funcionando com IQ Option E Pocket Option!**
