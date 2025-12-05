# 🚀 COMO INICIAR O GT SNIPER

## ⚠️ Problema: Python do Windows Store

O Python detectado no seu sistema é do **Windows Store** e pode causar conflitos.

---

## ✅ SOLUÇÃO 1: Usar PowerShell Diretamente

### 1. Abrir PowerShell como Administrador

```
Windows + X → Windows PowerShell (Admin)
```

### 2. Navegar até a pasta

```powershell
cd "c:\Users\benit\Downloads\GTSniper_WEB\GTSniper_WEB"
```

### 3. Executar o servidor

```powershell
python main.py
```

OU

```powershell
python3 main.py
```

### 4. Aguardar mensagem

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Abrir navegador

```
http://127.0.0.1:8000
```

---

## ✅ SOLUÇÃO 2: Instalar Python Real

### 1. Desabilitar alias do Windows Store

```
Windows → Configurações → Aplicativos
→ Configurações avançadas do aplicativo
→ Aliases de execução do aplicativo
→ Desligar "Python" e "Python3"
```

### 2. Baixar Python oficial

```
https://www.python.org/downloads/
```

### 3. Instalar com opções:

- ✅ **Add Python to PATH**
- ✅ **Install for all users**

### 4. Reiniciar terminal e executar:

```bash
cd "c:\Users\benit\Downloads\GTSniper_WEB\GTSniper_WEB"
python main.py
```

---

## ✅ SOLUÇÃO 3: Usar VS Code

### 1. Abrir pasta no VS Code

```
VS Code → File → Open Folder
→ Selecionar: GTSniper_WEB\GTSniper_WEB
```

### 2. Abrir terminal integrado

```
Ctrl + `
```

### 3. Executar

```bash
python main.py
```

---

## 🧪 Verificar se Funcionou

### No terminal, você deve ver:

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### No navegador (http://127.0.0.1:8000):

1. **Abrir DevTools (F12)**
2. **Console deve mostrar:**

```javascript
[BROKER PATCH] Inicializando patch de seleção de broker...
[BROKER PATCH] DOM carregado, procurando formulário de login...
[BROKER PATCH] Formulário de login encontrado!
[BROKER PATCH] Seletor de broker injetado com sucesso! ✅
```

3. **Tela de login deve ter:**

```
🏦 Selecione a Corretora
[IQ Option (Email + Senha) ▼]
```

---

## 🐛 Se ainda não funcionar

### Verificar se porta 8000 está livre:

```powershell
netstat -ano | findstr :8000
```

Se houver algo rodando, matar processo:

```powershell
taskkill /PID [NUMERO_DO_PID] /F
```

### Ou usar porta diferente:

Editar `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Mudar para 8001
```

Depois acessar: `http://127.0.0.1:8001`

---

## 📞 Logs de Debug

### Backend (Terminal):

```
INFO:     127.0.0.1:xxxxx - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "GET /assets/broker-selector-patch.js HTTP/1.1" 200 OK
```

### Frontend (F12 → Console):

```javascript
[BROKER PATCH] Seletor de broker injetado com sucesso! ✅
```

---

## ✅ Tudo Pronto?

Quando ver o seletor de broker na tela de login, está funcionando! 🎉

Siga o guia de testes: **[COMO_TESTAR.md](COMO_TESTAR.md)**

---

## 🚀 Comandos Rápidos

```powershell
# Navegar
cd "c:\Users\benit\Downloads\GTSniper_WEB\GTSniper_WEB"

# Iniciar
python main.py

# Parar (no terminal)
Ctrl + C
```

---

**Criado em:** 2025-12-05
**Status:** Pronto para uso manual
