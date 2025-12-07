"""
Binomo Broker Implementation
Usa BinomoAPI com autenticação email + senha
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base_broker import BaseBroker, BrokerType, AccountType


class BinomoBroker(BaseBroker):
    """
    Implementação do broker Binomo

    Usa a biblioteca BinomoAPI (ChipaDevTeam) com login via email + senha
    """

    def __init__(self):
        super().__init__()
        self.client = None
        self._binomo_available = False
        self._BinomoAPI = None

        # Tentar importar biblioteca
        try:
            from BinomoAPI import BinomoAPI
            self._BinomoAPI = BinomoAPI
            self._binomo_available = True
            self.log_info("BinomoAPI disponível")
        except ImportError:
            self.log_error("BinomoAPI não instalada")
            self.log_error("Instale com: pip install BinomoAPI")

    def get_broker_type(self) -> BrokerType:
        return BrokerType.BINOMO

    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Conectar ao Binomo com email + senha

        Args:
            credentials: {"email": "seu@email.com", "password": "senha"}

        Returns:
            True se conectou
        """
        if not self._binomo_available:
            self.log_error("BinomoAPI não disponível!")
            return False

        try:
            # Validar credenciais
            if not await self.validate_credentials(credentials):
                return False

            email = credentials.get("email")
            password = credentials.get("password")

            if not email or not password:
                self.log_error("Email e senha são obrigatórios")
                return False

            self.log_info(f"Conectando ao Binomo com {email}...")

            # Login (método estático retorna LoginResponse)
            try:
                login_response = self._BinomoAPI.login(email, password)
                self.log_info("Login bem-sucedido!")
            except Exception as e:
                self.log_error(f"Erro no login: {e}")
                return False

            # Criar cliente com auth token
            # Binomo usa async context manager
            try:
                # Determinar se é demo ou real
                demo = credentials.get("account_type", "PRACTICE") == "PRACTICE"

                # Criar cliente (será usado em async with)
                # Por enquanto, armazenar as credenciais
                self._auth_token = login_response.authtoken
                self._user_id = login_response.user_id
                self._demo = demo

                self.log_info(f"Cliente Binomo criado (demo={demo})")
                self._connected = True
                return True

            except Exception as e:
                self.log_error(f"Erro ao criar cliente: {e}")
                return False

        except Exception as e:
            self.log_error(f"Erro ao conectar: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def disconnect(self):
        """Desconectar do Binomo"""
        if self.client:
            try:
                # BinomoAPI usa context manager, então close automático
                self.client = None
                self._connected = False
                self.log_info("Desconectado do Binomo")
            except Exception as e:
                self.log_error(f"Erro ao desconectar: {e}")

    async def get_balance(self) -> float:
        """Obter saldo da conta"""
        if not self.is_connected:
            self.log_error("Não conectado")
            return 0.0

        try:
            # Criar cliente temporário para operação
            async with self._BinomoAPI(
                auth_token=self._auth_token,
                device_id=self._user_id,
                demo=self._demo
            ) as api:
                balance = await api.get_balance()
                return float(balance.amount)
        except Exception as e:
            self.log_error(f"Erro ao obter saldo: {e}")
            return 0.0

    async def get_candles(self, asset: str, timeframe: int, count: int) -> List[Dict]:
        """
        Obter candles históricos

        Args:
            asset: Par (ex: "EURUSD")
            timeframe: Timeframe em segundos
            count: Quantidade de candles

        Returns:
            Lista de candles normalizados
        """
        if not self.is_connected:
            self.log_error("Não conectado")
            return []

        try:
            async with self._BinomoAPI(
                auth_token=self._auth_token,
                device_id=self._user_id,
                demo=self._demo
            ) as api:
                # Obter candles
                candles = await api.get_candles(
                    asset=asset,
                    period=timeframe,
                    count=count
                )

                # Normalizar formato
                normalized = []
                for candle in candles:
                    normalized.append({
                        "time": candle.get("time") or candle.get("timestamp"),
                        "open": float(candle.get("open", 0)),
                        "close": float(candle.get("close", 0)),
                        "high": float(candle.get("high", 0)),
                        "low": float(candle.get("low", 0)),
                        "volume": float(candle.get("volume", 0))
                    })

                return normalized

        except Exception as e:
            self.log_error(f"Erro ao obter candles: {e}")
            return []

    async def buy(self, asset: str, amount: float, direction: str, duration: int) -> Dict[str, Any]:
        """
        Abrir ordem

        Args:
            asset: Par
            amount: Valor em dinheiro
            direction: "CALL" ou "PUT"
            duration: Duração em segundos

        Returns:
            Resultado da ordem
        """
        if not self.is_connected:
            return {"success": False, "message": "Não conectado"}

        try:
            async with self._BinomoAPI(
                auth_token=self._auth_token,
                device_id=self._user_id,
                demo=self._demo
            ) as api:
                # Binomo usa "up" e "down"
                binomo_direction = "up" if direction.upper() == "CALL" else "down"

                # Abrir ordem
                result = await api.buy(
                    asset=asset,
                    amount=amount,
                    direction=binomo_direction,
                    duration=duration
                )

                return {
                    "success": True,
                    "order_id": result.get("id"),
                    "message": "Ordem aberta com sucesso"
                }

        except Exception as e:
            self.log_error(f"Erro ao abrir ordem: {e}")
            return {"success": False, "message": str(e)}

    async def get_available_assets(self) -> List[str]:
        """Obter lista de ativos disponíveis"""
        if not self.is_connected:
            return []

        try:
            async with self._BinomoAPI(
                auth_token=self._auth_token,
                device_id=self._user_id,
                demo=self._demo
            ) as api:
                assets = await api.get_available_assets()
                return [asset.get("name") for asset in assets]
        except Exception as e:
            self.log_error(f"Erro ao obter ativos: {e}")
            return []

    async def switch_account(self, account_type: str) -> bool:
        """
        Trocar tipo de conta

        Args:
            account_type: "PRACTICE" ou "REAL"

        Returns:
            True se trocou
        """
        try:
            self._demo = (account_type == "PRACTICE")
            self.log_info(f"Conta alterada para: {account_type}")
            return True
        except Exception as e:
            self.log_error(f"Erro ao trocar conta: {e}")
            return False


# Auto-registrar no factory
from ..broker_factory import BrokerFactory
BrokerFactory.register(BinomoBroker)
