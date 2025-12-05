"""
Base Broker - Classe Abstrata para Todas as Corretoras
Define interface comum que todas as corretoras devem implementar
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BrokerType(Enum):
    """Tipos de corretoras suportadas"""
    IQOPTION = "iqoption"
    POCKETOPTION = "pocketoption"
    QUOTEX = "quotex"  # Futuro
    BINOMO = "binomo"  # Futuro


class AccountType(Enum):
    """Tipos de conta"""
    PRACTICE = "PRACTICE"
    REAL = "REAL"


class BaseBroker(ABC):
    """
    Classe abstrata para todas as corretoras

    Todas as corretoras devem implementar estes métodos
    para garantir compatibilidade com o scanner
    """

    def __init__(self):
        self.connected = False
        self.balance = 0.0
        self.account_type = AccountType.PRACTICE
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Conectar à corretora

        Args:
            credentials: Credenciais específicas da corretora
                - IQ Option: {"email": "...", "password": "..."}
                - Pocket Option: {"ssid": "..."}

        Returns:
            True se conectou com sucesso
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Desconectar da corretora

        Returns:
            True se desconectou com sucesso
        """
        pass

    @abstractmethod
    async def check_connection(self) -> bool:
        """
        Verificar se está conectado

        Returns:
            True se está conectado
        """
        pass

    @abstractmethod
    async def get_balance(self) -> float:
        """
        Obter saldo atual

        Returns:
            Saldo da conta
        """
        pass

    @abstractmethod
    async def switch_account(self, account_type: str) -> bool:
        """
        Mudar tipo de conta (PRACTICE/REAL)

        Args:
            account_type: "PRACTICE" ou "REAL"

        Returns:
            True se mudou com sucesso
        """
        pass

    @abstractmethod
    async def get_candles(self, asset: str, timeframe: int, count: int) -> List[Dict]:
        """
        Obter candles históricos

        Args:
            asset: Nome do ativo (ex: "EURUSD")
            timeframe: Timeframe em segundos (ex: 60)
            count: Quantidade de candles

        Returns:
            Lista de candles no formato:
            [
                {
                    "time": timestamp,
                    "open": float,
                    "close": float,
                    "high": float,
                    "low": float,
                    "volume": float
                },
                ...
            ]
        """
        pass

    @abstractmethod
    async def buy(
        self,
        asset: str,
        amount: float,
        direction: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Executar ordem de compra

        Args:
            asset: Nome do ativo
            amount: Valor da operação
            direction: "CALL" ou "PUT"
            duration: Duração em segundos

        Returns:
            {
                "success": bool,
                "order_id": str,
                "message": str,
                "error": str (se houver)
            }
        """
        pass

    @abstractmethod
    async def get_available_assets(self) -> List[str]:
        """
        Obter lista de ativos disponíveis

        Returns:
            Lista de nomes de ativos
        """
        pass

    @abstractmethod
    async def get_asset_info(self, asset: str) -> Optional[Dict]:
        """
        Obter informações sobre um ativo

        Args:
            asset: Nome do ativo

        Returns:
            {
                "name": str,
                "enabled": bool,
                "tradeable": bool,
                "min_amount": float,
                "max_amount": float,
                "profit": float
            }
        """
        pass

    @abstractmethod
    def get_broker_name(self) -> str:
        """
        Nome da corretora

        Returns:
            Nome para exibição (ex: "IQ Option", "Pocket Option")
        """
        pass

    @abstractmethod
    def get_broker_type(self) -> BrokerType:
        """
        Tipo da corretora

        Returns:
            BrokerType enum
        """
        pass

    # Métodos auxiliares (não precisam ser implementados)

    def is_connected(self) -> bool:
        """Verifica se está conectado (método auxiliar)"""
        return self.connected

    def get_current_balance(self) -> float:
        """Retorna saldo atual em cache"""
        return self.balance

    def get_account_type(self) -> str:
        """Retorna tipo de conta atual"""
        return self.account_type.value

    async def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Validar credenciais antes de conectar

        Args:
            credentials: Credenciais a validar

        Returns:
            True se válidas
        """
        # Implementação padrão - pode ser sobrescrita
        if not credentials:
            self.logger.error("Credenciais vazias")
            return False
        return True

    def log_info(self, message: str):
        """Log de informação"""
        self.logger.info(f"[{self.get_broker_name()}] {message}")

    def log_error(self, message: str):
        """Log de erro"""
        self.logger.error(f"[{self.get_broker_name()}] {message}")

    def log_warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(f"[{self.get_broker_name()}] {message}")
