# 🎯 PLANO: SUPORTE A MÚLTIPLAS CORRETORAS

**Data:** 04/12/2024
**Objetivo:** Adicionar Pocket Option SEM quebrar IQ Option existente

---

## 📋 ARQUITETURA PROPOSTA

### Estrutura de Pastas:
```
app/
├── services/
│   ├── brokers/                    # NOVO - Abstração de corretoras
│   │   ├── __init__.py
│   │   ├── base_broker.py         # Classe abstrata
│   │   ├── broker_factory.py      # Factory pattern
│   │   ├── iqoption/              # IQ Option (mover código existente)
│   │   │   ├── __init__.py
│   │   │   ├── iqoption_broker.py
│   │   │   └── iqoption_client.py # Cliente existente
│   │   └── pocketoption/          # NOVO - Pocket Option
│   │       ├── __init__.py
│   │       ├── pocketoption_broker.py
│   │       └── pocketoption_client.py
│   │
│   ├── iqoption/                   # MANTÉM - código legado
│   ├── iqoptionapi/                # MANTÉM - API existente
│   └── scanner/                    # MANTÉM - usar brokers abstratos
```

---

## 🏗️ COMPONENTES

### 1. BaseBroker (Classe Abstrata)

Define interface comum para todas as corretoras:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from enum import Enum

class BrokerType(Enum):
    IQOPTION = "iqoption"
    POCKETOPTION = "pocketoption"
    QUOTEX = "quotex"  # Futuro
    BINOMO = "binomo"  # Futuro

class BaseBroker(ABC):
    """Classe abstrata para todas as corretoras"""

    def __init__(self):
        self.connected = False
        self.balance = 0.0
        self.account_type = "PRACTICE"

    @abstractmethod
    async def connect(self, credentials: Dict) -> bool:
        """Conectar à corretora"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Desconectar da corretora"""
        pass

    @abstractmethod
    async def get_balance(self) -> float:
        """Obter saldo"""
        pass

    @abstractmethod
    async def switch_account(self, account_type: str) -> bool:
        """Mudar conta (PRACTICE/REAL)"""
        pass

    @abstractmethod
    async def get_candles(self, asset: str, timeframe: int, count: int) -> List:
        """Obter candles históricos"""
        pass

    @abstractmethod
    async def buy(self, asset: str, amount: float, direction: str, duration: int) -> Dict:
        """Executar ordem"""
        pass

    @abstractmethod
    async def get_available_assets(self) -> List[str]:
        """Obter ativos disponíveis"""
        pass

    @abstractmethod
    def get_broker_name(self) -> str:
        """Nome da corretora"""
        pass
```

---

### 2. IQOptionBroker (Adapter)

Adapta o código existente para nova interface:

```python
from .base_broker import BaseBroker, BrokerType
from app.services.iqoption.iqoption_client import IQOptionClient

class IQOptionBroker(BaseBroker):
    """Adapter para IQ Option mantendo código existente"""

    def __init__(self):
        super().__init__()
        self.client = None

    async def connect(self, credentials: Dict) -> bool:
        """
        credentials = {
            "email": "usuario@email.com",
            "password": "senha"
        }
        """
        try:
            self.client = IQOptionClient(
                credentials["email"],
                credentials["password"]
            )
            success = await self.client.connect()
            self.connected = success
            return success
        except Exception as e:
            print(f"Erro ao conectar IQ Option: {e}")
            return False

    async def disconnect(self) -> bool:
        if self.client:
            await self.client.disconnect()
        self.connected = False
        return True

    async def get_balance(self) -> float:
        if not self.client:
            return 0.0
        balance = await self.client.get_balance()
        self.balance = balance
        return balance

    async def switch_account(self, account_type: str) -> bool:
        if not self.client:
            return False
        success = await self.client.change_balance(account_type)
        self.account_type = account_type
        return success

    async def get_candles(self, asset: str, timeframe: int, count: int) -> List:
        if not self.client:
            return []
        return await self.client.get_candles(asset, timeframe, count)

    async def buy(self, asset: str, amount: float, direction: str, duration: int) -> Dict:
        if not self.client:
            return {"success": False, "error": "Not connected"}

        # Converter para formato IQ Option
        action = "call" if direction.upper() == "CALL" else "put"

        result = await self.client.buy(
            amount=amount,
            active=asset,
            direction=action,
            duration=duration
        )

        return {
            "success": result.get("success", False),
            "order_id": result.get("id"),
            "message": result.get("message", "")
        }

    async def get_available_assets(self) -> List[str]:
        if not self.client:
            return []
        assets = await self.client.get_all_open_time()
        return [a["name"] for a in assets if a["open"]]

    def get_broker_name(self) -> str:
        return "IQ Option"
```

---

### 3. PocketOptionBroker (Nova Implementação)

```python
from .base_broker import BaseBroker, BrokerType
from pocketoptionapi.stable_api import PocketOption

class PocketOptionBroker(BaseBroker):
    """Implementação para Pocket Option"""

    def __init__(self):
        super().__init__()
        self.client = None

    async def connect(self, credentials: Dict) -> bool:
        """
        credentials = {
            "ssid": "SESSION_ID_DO_NAVEGADOR"
        }
        """
        try:
            self.client = PocketOption(ssid=credentials["ssid"])
            success = self.client.connect()
            self.connected = success

            if success:
                self.balance = await self.get_balance()

            return success
        except Exception as e:
            print(f"Erro ao conectar Pocket Option: {e}")
            return False

    async def disconnect(self) -> bool:
        if self.client:
            self.client.close()
        self.connected = False
        return True

    async def get_balance(self) -> float:
        if not self.client:
            return 0.0
        balance = self.client.get_balance()
        self.balance = balance
        return balance

    async def switch_account(self, account_type: str) -> bool:
        if not self.client:
            return False
        # Pocket Option: "PRACTICE" ou "REAL"
        success = self.client.change_account(account_type)
        if success:
            self.account_type = account_type
        return success

    async def get_candles(self, asset: str, timeframe: int, count: int) -> List:
        if not self.client:
            return []

        # Converter timeframe para formato Pocket Option
        candles = self.client.get_candles(asset, timeframe, count)

        # Normalizar formato (compatível com IQ Option)
        normalized = []
        for candle in candles:
            normalized.append({
                "open": candle["open"],
                "close": candle["close"],
                "high": candle["max"],
                "low": candle["min"],
                "volume": candle.get("volume", 0),
                "time": candle["time"]
            })

        return normalized

    async def buy(self, asset: str, amount: float, direction: str, duration: int) -> Dict:
        if not self.client:
            return {"success": False, "error": "Not connected"}

        try:
            # Pocket Option: "call" ou "put"
            action = "call" if direction.upper() == "CALL" else "put"

            # Executar ordem
            result = self.client.buy(
                amount=amount,
                asset=asset,
                direction=action,
                duration=duration
            )

            return {
                "success": result.get("isSuccessful", False),
                "order_id": result.get("id"),
                "message": result.get("message", "")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_available_assets(self) -> List[str]:
        if not self.client:
            return []

        try:
            assets = self.client.get_all_asset()
            return [a["name"] for a in assets if a.get("enabled", True)]
        except:
            return []

    def get_broker_name(self) -> str:
        return "Pocket Option"
```

---

### 4. BrokerFactory

```python
from typing import Optional
from .base_broker import BaseBroker, BrokerType
from .iqoption.iqoption_broker import IQOptionBroker
from .pocketoption.pocketoption_broker import PocketOptionBroker

class BrokerFactory:
    """Factory para criar instâncias de brokers"""

    _brokers = {
        BrokerType.IQOPTION: IQOptionBroker,
        BrokerType.POCKETOPTION: PocketOptionBroker,
        # Futuro:
        # BrokerType.QUOTEX: QuotexBroker,
        # BrokerType.BINOMO: BinomoBroker,
    }

    @staticmethod
    def create_broker(broker_type: str) -> Optional[BaseBroker]:
        """
        Criar instância de broker

        Args:
            broker_type: "iqoption", "pocketoption", etc.

        Returns:
            Instância do broker ou None se inválido
        """
        try:
            broker_enum = BrokerType(broker_type.lower())
            broker_class = BrokerFactory._brokers.get(broker_enum)

            if broker_class:
                return broker_class()
            else:
                raise ValueError(f"Broker '{broker_type}' não implementado")
        except ValueError as e:
            print(f"Erro ao criar broker: {e}")
            return None

    @staticmethod
    def get_available_brokers() -> List[str]:
        """Retorna lista de brokers disponíveis"""
        return [broker.value for broker in BrokerType]

    @staticmethod
    def get_broker_display_names() -> Dict[str, str]:
        """Retorna nomes de exibição dos brokers"""
        return {
            "iqoption": "IQ Option",
            "pocketoption": "Pocket Option",
            # Futuro:
            # "quotex": "Quotex",
            # "binomo": "Binomo",
        }
```

---

## 🔌 INTEGRAÇÃO COM SCANNER

### Atualizar Scanner para usar BaseBroker:

```python
# app/services/scanner/auto_scanner.py

from app.services.brokers.base_broker import BaseBroker

class AutoScanner:
    def __init__(self, broker: BaseBroker):
        self.broker = broker  # Agora recebe qualquer broker!
        self.running = False

    async def scan_for_signals(self):
        """Escanear usando broker abstrato"""
        if not self.broker.connected:
            return []

        # Obter ativos disponíveis
        assets = await self.broker.get_available_assets()

        signals = []
        for asset in assets:
            # Obter candles
            candles = await self.broker.get_candles(asset, 60, 100)

            # Analisar com indicadores técnicos
            signal = self.analyze_candles(candles, asset)

            if signal:
                signals.append(signal)

        return signals
```

---

## 🎨 FRONTEND - Seleção de Corretora

### Tela de Login Atualizada:

```typescript
// Login.tsx

interface LoginForm {
  broker: 'iqoption' | 'pocketoption';
  email?: string;      // IQ Option
  password?: string;   // IQ Option
  ssid?: string;       // Pocket Option
}

const Login = () => {
  const [broker, setBroker] = useState<string>('iqoption');

  return (
    <div>
      {/* Seleção de Corretora */}
      <select onChange={(e) => setBroker(e.target.value)} value={broker}>
        <option value="iqoption">IQ Option</option>
        <option value="pocketoption">Pocket Option</option>
      </select>

      {/* Campos específicos por corretora */}
      {broker === 'iqoption' && (
        <>
          <input type="email" placeholder="Email" />
          <input type="password" placeholder="Senha" />
        </>
      )}

      {broker === 'pocketoption' && (
        <>
          <input type="text" placeholder="SSID (Session ID)" />
          <small>Copie do navegador: Application → Cookies → ssid</small>
        </>
      )}

      <button onClick={handleLogin}>Conectar</button>
    </div>
  );
};
```

---

## 🔧 API ROUTES ATUALIZADAS

### Login Endpoint:

```python
# app/api/routes.py

from app.services.brokers.broker_factory import BrokerFactory

@router.post("/login")
async def login(request: LoginRequest):
    """Login com seleção de corretora"""

    # Criar broker apropriado
    broker = BrokerFactory.create_broker(request.broker_type)

    if not broker:
        raise HTTPException(400, "Corretora inválida")

    # Conectar com credenciais específicas
    credentials = {}

    if request.broker_type == "iqoption":
        credentials = {
            "email": request.email,
            "password": request.password
        }
    elif request.broker_type == "pocketoption":
        credentials = {
            "ssid": request.ssid
        }

    # Conectar
    success = await broker.connect(credentials)

    if success:
        # Salvar broker na sessão
        session_manager.set_broker(session_id, broker)

        return {
            "success": True,
            "broker": broker.get_broker_name(),
            "balance": await broker.get_balance()
        }
    else:
        raise HTTPException(401, "Falha ao conectar")
```

---

## 📦 DEPENDÊNCIAS

### requirements.txt - ADICIONAR:

```txt
# Pocket Option API
git+https://github.com/ChipaDevTeam/PocketOptionAPI.git
```

---

## ✅ VANTAGENS DESTA ARQUITETURA

1. **✅ NÃO QUEBRA NADA:**
   - IQ Option continua funcionando EXATAMENTE como antes
   - Código legado mantido intacto

2. **✅ ESCALÁVEL:**
   - Adicionar nova corretora = criar novo broker
   - Não precisa mexer no scanner

3. **✅ CLEAN CODE:**
   - Interface comum (BaseBroker)
   - Factory Pattern
   - Separação de responsabilidades

4. **✅ FÁCIL MANUTENÇÃO:**
   - Cada corretora em sua pasta
   - Código isolado e testável

5. **✅ USUÁRIO ESCOLHE:**
   - No login, seleciona corretora
   - Sistema usa broker correto automaticamente

---

## 🚀 ORDEM DE IMPLEMENTAÇÃO

### Fase 1: Estrutura Base (1-2 horas)
- [ ] Criar pasta `app/services/brokers/`
- [ ] Criar `base_broker.py`
- [ ] Criar `broker_factory.py`

### Fase 2: Adaptar IQ Option (1 hora)
- [ ] Criar `iqoption/iqoption_broker.py`
- [ ] Mover código existente
- [ ] Testar que continua funcionando

### Fase 3: Implementar Pocket Option (2-3 horas)
- [ ] Instalar biblioteca
- [ ] Criar `pocketoption/pocketoption_broker.py`
- [ ] Testar conexão

### Fase 4: Atualizar Scanner (1 hora)
- [ ] Modificar para usar `BaseBroker`
- [ ] Testar com ambas corretoras

### Fase 5: Frontend (1-2 horas)
- [ ] Adicionar seleção de corretora no login
- [ ] Campos específicos por corretora
- [ ] Validação

### Fase 6: Testes (1 hora)
- [ ] Testar IQ Option (não deve quebrar!)
- [ ] Testar Pocket Option
- [ ] Testar switch entre corretoras

**TOTAL:** ~7-10 horas de trabalho

---

## 🎯 RESULTADO FINAL

```
Usuário acessa sistema
    ↓
Tela de Login
    ↓
Seleciona: [ IQ Option ▼ ]  ou  [ Pocket Option ▼ ]
    ↓
Campos mudam automaticamente
    ↓
Conecta
    ↓
Scanner usa broker correto
    ↓
Sinais gerados para corretora escolhida!
```

---

**ARQUITETURA APROVADA?**
**Posso começar a implementar?**

---

_Planejamento: 04/12/2024_
_Status: Aguardando aprovação para implementar_
