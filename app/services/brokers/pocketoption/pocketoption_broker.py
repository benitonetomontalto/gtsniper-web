"""
Pocket Option Broker
Implementação completa para Pocket Option usando API não oficial
"""
from typing import Dict, List, Optional, Any
from ..base_broker import BaseBroker, BrokerType, AccountType
import logging

logger = logging.getLogger(__name__)


class PocketOptionBroker(BaseBroker):
    """
    Implementação para Pocket Option

    Requer biblioteca: pocketoptionapi
    Autenticação: SSID (Session ID do navegador)
    """

    def __init__(self):
        super().__init__()
        self.client = None
        self._pocketoption_available = False

        # Tentar importar biblioteca
        try:
            from pocketoptionapi.stable_api import PocketOption
            self._PocketOption = PocketOption
            self._pocketoption_available = True
            self.log_info("Biblioteca Pocket Option disponível")
        except ImportError:
            self.log_warning("Biblioteca pocketoptionapi não instalada")
            self._PocketOption = None

    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Conectar à Pocket Option

        Args:
            credentials: {"ssid": "SESSION_ID_DO_NAVEGADOR"}

        Como obter SSID:
            1. Abrir https://pocketoption.com no navegador
            2. F12 (DevTools) → Application → Cookies
            3. Copiar valor do cookie "ssid"

        Returns:
            True se conectou
        """
        if not self._pocketoption_available:
            self.log_error("Biblioteca pocketoptionapi não instalada!")
            self.log_error("Instale com: pip install git+https://github.com/ChipaDevTeam/PocketOptionAPI.git")
            return False

        try:
            # Validar credenciais
            if not await self.validate_credentials(credentials):
                return False

            ssid = credentials.get("ssid")
            if not ssid:
                self.log_error("SSID não fornecido")
                return False

            self.log_info("Conectando com SSID...")

            # Criar cliente Pocket Option
            self.client = self._PocketOption(ssid=ssid)

            # Conectar (sync na biblioteca original)
            try:
                success = self.client.connect()
            except Exception as e:
                self.log_error(f"Erro ao conectar: {e}")
                success = False

            if success:
                self.connected = True

                # Obter saldo inicial
                try:
                    self.balance = await self.get_balance()
                    self.log_info(f"Conectado com sucesso! Saldo: ${self.balance}")
                except:
                    self.balance = 0.0
                    self.log_warning("Conectado mas não conseguiu obter saldo")
            else:
                self.log_error("Falha ao conectar - SSID inválido?")
                self.connected = False

            return success

        except Exception as e:
            self.log_error(f"Erro ao conectar: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> bool:
        """Desconectar da Pocket Option"""
        try:
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
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
            balance = self.client.get_balance()
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
            balance = self.client.get_balance()
            self.balance = float(balance) if balance else 0.0
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
            # Pocket Option usa change_account()
            success = self.client.change_account(account_type)

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
            # Pocket Option get_candles
            candles = self.client.get_candles(asset, timeframe, count)

            if not candles:
                return []

            # Normalizar formato (compatível com IQ Option)
            normalized = []
            for candle in candles:
                normalized.append({
                    "time": candle.get("time", candle.get("from", 0)),
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
            # Converter direção para formato Pocket Option
            action = "call" if direction.upper() == "CALL" else "put"

            self.log_info(f"Comprando {asset} {action.upper()} ${amount} por {duration}s")

            # Executar ordem
            result = self.client.buy(
                amount=amount,
                asset=asset,
                direction=action,
                duration=duration
            )

            success = result.get("isSuccessful", False) or result.get("success", False)

            response = {
                "success": success,
                "order_id": result.get("id", result.get("order_id")),
                "message": result.get("message", "")
            }

            if not success:
                response["error"] = result.get("message", result.get("error", "Unknown error"))

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
            assets = self.client.get_all_asset()

            if not assets:
                return []

            # Filtrar apenas ativos habilitados
            available = [
                asset["name"]
                for asset in assets
                if asset.get("enabled", True) and asset.get("open", True)
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
            assets = self.client.get_all_asset()

            if not assets:
                return None

            for a in assets:
                if a.get("name") == asset:
                    return {
                        "name": a.get("name"),
                        "enabled": a.get("enabled", True),
                        "tradeable": a.get("open", True),
                        "min_amount": a.get("min_amount", 1.0),
                        "max_amount": a.get("max_amount", 1000.0),
                        "profit": a.get("profit", 0.0)
                    }

            return None

        except Exception as e:
            self.log_error(f"Erro ao obter info do ativo: {e}")
            return None

    def get_broker_name(self) -> str:
        """Nome para exibição"""
        return "Pocket Option"

    def get_broker_type(self) -> BrokerType:
        """Tipo da corretora"""
        return BrokerType.POCKETOPTION

    async def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validar credenciais Pocket Option"""
        if not credentials:
            self.log_error("Credenciais vazias")
            return False

        ssid = credentials.get("ssid")

        if not ssid:
            self.log_error("SSID faltando")
            return False

        if len(ssid) < 10:
            self.log_error("SSID muito curto - provavelmente inválido")
            return False

        return True

    def get_ssid_instructions(self) -> str:
        """
        Retorna instruções de como obter SSID

        Returns:
            Texto com instruções
        """
        return """
        COMO OBTER SSID DA POCKET OPTION:

        1. Abra https://pocketoption.com no navegador
        2. Faça login normalmente
        3. Pressione F12 para abrir DevTools
        4. Vá na aba "Application" (Chrome) ou "Storage" (Firefox)
        5. No menu lateral, expanda "Cookies"
        6. Clique em "https://pocketoption.com"
        7. Procure o cookie chamado "ssid"
        8. Copie o VALOR do cookie (string longa)
        9. Cole aqui no campo SSID

        IMPORTANTE:
        - O SSID expira após algumas horas
        - Você precisará renovar quando expirar
        - Não compartilhe seu SSID (é como uma senha)
        """
