"""
IQ Option Broker - Adapter
Adapta código existente da IQ Option para interface BaseBroker
NÃO mexe no código legado - apenas traduz para interface comum
"""
from typing import Dict, List, Optional, Any
from ..base_broker import BaseBroker, BrokerType, AccountType
from app.services.iqoption.iqoption_client import IQOptionClient
import logging

logger = logging.getLogger(__name__)


class IQOptionBroker(BaseBroker):
    """
    Adapter para IQ Option

    Usa o código existente (IQOptionClient) mas implementa
    a interface BaseBroker para compatibilidade
    """

    def __init__(self):
        super().__init__()
        self.client: Optional[IQOptionClient] = None
        self.log_info("IQ Option Broker inicializado")

    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Conectar à IQ Option

        Args:
            credentials: {"email": "...", "password": "..."}

        Returns:
            True se conectou
        """
        try:
            # Validar credenciais
            if not await self.validate_credentials(credentials):
                return False

            email = credentials.get("email")
            password = credentials.get("password")

            if not email or not password:
                self.log_error("Email ou senha não fornecidos")
                return False

            self.log_info(f"Conectando com email: {email}")

            # Criar cliente IQ Option (código existente)
            self.client = IQOptionClient(email, password)

            # Conectar
            success = await self.client.connect()

            if success:
                self.connected = True
                self.balance = await self.get_balance()
                self.log_info(f"Conectado com sucesso! Saldo: ${self.balance}")
            else:
                self.log_error("Falha ao conectar")
                self.connected = False

            return success

        except Exception as e:
            self.log_error(f"Erro ao conectar: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> bool:
        """Desconectar da IQ Option"""
        try:
            if self.client:
                await self.client.disconnect()
                self.log_info("Desconectado")

            self.connected = False
            self.client = None
            return True

        except Exception as e:
            self.log_error(f"Erro ao desconectar: {e}")
            return False

    async def check_connection(self) -> bool:
        """Verificar se está conectado"""
        if not self.client:
            return False

        try:
            # Tentar obter saldo para verificar conexão
            balance = await self.client.get_balance()
            self.connected = balance is not None
            return self.connected
        except:
            self.connected = False
            return False

    async def get_balance(self) -> float:
        """Obter saldo atual"""
        if not self.client:
            return 0.0

        try:
            balance = await self.client.get_balance()
            self.balance = balance if balance else 0.0
            return self.balance
        except Exception as e:
            self.log_error(f"Erro ao obter saldo: {e}")
            return 0.0

    async def switch_account(self, account_type: str) -> bool:
        """
        Mudar tipo de conta

        Args:
            account_type: "PRACTICE" ou "REAL"
        """
        if not self.client:
            return False

        try:
            success = await self.client.change_balance(account_type)

            if success:
                self.account_type = AccountType(account_type)
                self.balance = await self.get_balance()
                self.log_info(f"Conta alterada para {account_type}. Saldo: ${self.balance}")
            else:
                self.log_error(f"Falha ao mudar para conta {account_type}")

            return success

        except Exception as e:
            self.log_error(f"Erro ao mudar conta: {e}")
            return False

    async def get_candles(self, asset: str, timeframe: int, count: int) -> List[Dict]:
        """
        Obter candles históricos

        Args:
            asset: Nome do ativo (ex: "EURUSD")
            timeframe: Timeframe em segundos (ex: 60)
            count: Quantidade de candles

        Returns:
            Lista de candles normalizados
        """
        if not self.client:
            return []

        try:
            candles = await self.client.get_candles(asset, timeframe, count)

            # Normalizar formato
            normalized = []
            for candle in candles:
                normalized.append({
                    "time": candle.get("from", candle.get("time", 0)),
                    "open": float(candle.get("open", 0)),
                    "close": float(candle.get("close", 0)),
                    "high": float(candle.get("max", candle.get("high", 0))),
                    "low": float(candle.get("min", candle.get("low", 0))),
                    "volume": float(candle.get("volume", 0))
                })

            return normalized

        except Exception as e:
            self.log_error(f"Erro ao obter candles: {e}")
            return []

    async def buy(
        self,
        asset: str,
        amount: float,
        direction: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Executar ordem

        Args:
            asset: Nome do ativo
            amount: Valor da operação
            direction: "CALL" ou "PUT"
            duration: Duração em segundos
        """
        if not self.client:
            return {
                "success": False,
                "error": "Not connected"
            }

        try:
            # Converter direção para formato IQ Option
            action = "call" if direction.upper() == "CALL" else "put"

            self.log_info(f"Comprando {asset} {action.upper()} ${amount} por {duration}s")

            # Executar ordem (código existente)
            result = await self.client.buy(
                amount=amount,
                active=asset,
                direction=action,
                duration=duration
            )

            success = result.get("success", False) or result.get("isSuccessful", False)

            response = {
                "success": success,
                "order_id": result.get("id", result.get("order_id")),
                "message": result.get("message", "")
            }

            if not success:
                response["error"] = result.get("message", "Unknown error")

            if success:
                self.log_info(f"Ordem executada: #{response['order_id']}")
            else:
                self.log_error(f"Ordem falhou: {response.get('error')}")

            return response

        except Exception as e:
            self.log_error(f"Erro ao executar ordem: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_available_assets(self) -> List[str]:
        """Obter lista de ativos disponíveis"""
        if not self.client:
            return []

        try:
            assets = await self.client.get_all_open_time()

            # Filtrar apenas ativos abertos
            available = [
                asset["name"]
                for asset in assets
                if asset.get("open", False)
            ]

            return available

        except Exception as e:
            self.log_error(f"Erro ao obter ativos: {e}")
            return []

    async def get_asset_info(self, asset: str) -> Optional[Dict]:
        """Obter informações sobre um ativo"""
        if not self.client:
            return None

        try:
            assets = await self.client.get_all_open_time()

            for a in assets:
                if a.get("name") == asset:
                    return {
                        "name": a.get("name"),
                        "enabled": a.get("open", False),
                        "tradeable": a.get("open", False),
                        "min_amount": 1.0,  # IQ Option default
                        "max_amount": 1000.0,  # IQ Option default
                        "profit": a.get("profit", 0.0)
                    }

            return None

        except Exception as e:
            self.log_error(f"Erro ao obter info do ativo: {e}")
            return None

    def get_broker_name(self) -> str:
        """Nome para exibição"""
        return "IQ Option"

    def get_broker_type(self) -> BrokerType:
        """Tipo da corretora"""
        return BrokerType.IQOPTION

    async def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validar credenciais IQ Option"""
        if not credentials:
            self.log_error("Credenciais vazias")
            return False

        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            self.log_error("Email ou senha faltando")
            return False

        if "@" not in email:
            self.log_error("Email inválido")
            return False

        if len(password) < 6:
            self.log_error("Senha muito curta")
            return False

        return True
