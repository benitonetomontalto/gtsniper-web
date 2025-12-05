"""
Broker Factory - Cria instâncias de brokers
Factory Pattern para gerenciar criação de diferentes corretoras
"""
from typing import Optional, Dict, List
from .base_broker import BaseBroker, BrokerType
import logging

logger = logging.getLogger(__name__)


class BrokerFactory:
    """
    Factory para criar instâncias de brokers

    Uso:
        broker = BrokerFactory.create_broker("iqoption")
        await broker.connect(credentials)
    """

    # Registry de brokers disponíveis
    _brokers: Dict[BrokerType, type] = {}

    @classmethod
    def register_broker(cls, broker_type: BrokerType, broker_class: type):
        """
        Registrar um novo broker

        Args:
            broker_type: Tipo do broker (BrokerType enum)
            broker_class: Classe do broker
        """
        cls._brokers[broker_type] = broker_class
        logger.info(f"Broker registrado: {broker_type.value} -> {broker_class.__name__}")

    @classmethod
    def create_broker(cls, broker_type: str) -> Optional[BaseBroker]:
        """
        Criar instância de broker

        Args:
            broker_type: String do tipo ("iqoption", "pocketoption", etc.)

        Returns:
            Instância do broker ou None se inválido

        Exemplo:
            broker = BrokerFactory.create_broker("iqoption")
            if broker:
                await broker.connect({"email": "...", "password": "..."})
        """
        try:
            # Converter string para enum
            broker_enum = BrokerType(broker_type.lower())

            # Buscar classe do broker
            broker_class = cls._brokers.get(broker_enum)

            if broker_class:
                logger.info(f"Criando broker: {broker_type}")
                return broker_class()
            else:
                logger.error(f"Broker '{broker_type}' não está registrado")
                return None

        except ValueError as e:
            logger.error(f"Tipo de broker inválido: {broker_type}")
            return None
        except Exception as e:
            logger.error(f"Erro ao criar broker: {e}")
            return None

    @classmethod
    def get_available_brokers(cls) -> List[str]:
        """
        Retorna lista de brokers disponíveis

        Returns:
            Lista de strings ["iqoption", "pocketoption", ...]
        """
        return [broker.value for broker in cls._brokers.keys()]

    @classmethod
    def get_broker_display_names(cls) -> Dict[str, str]:
        """
        Retorna nomes de exibição dos brokers

        Returns:
            {"iqoption": "IQ Option", "pocketoption": "Pocket Option", ...}
        """
        display_names = {}

        for broker_type, broker_class in cls._brokers.items():
            try:
                # Criar instância temporária para pegar o nome
                instance = broker_class()
                display_names[broker_type.value] = instance.get_broker_name()
            except:
                # Fallback se não conseguir criar instância
                display_names[broker_type.value] = broker_type.value.title()

        return display_names

    @classmethod
    def is_broker_available(cls, broker_type: str) -> bool:
        """
        Verificar se um broker está disponível

        Args:
            broker_type: String do tipo

        Returns:
            True se está disponível
        """
        try:
            broker_enum = BrokerType(broker_type.lower())
            return broker_enum in cls._brokers
        except:
            return False

    @classmethod
    def get_broker_info(cls) -> List[Dict]:
        """
        Retorna informações sobre todos os brokers

        Returns:
            [
                {
                    "type": "iqoption",
                    "name": "IQ Option",
                    "available": True
                },
                ...
            ]
        """
        info = []

        for broker_type in BrokerType:
            try:
                is_available = broker_type in cls._brokers

                if is_available:
                    broker_class = cls._brokers[broker_type]
                    instance = broker_class()
                    name = instance.get_broker_name()
                else:
                    name = broker_type.value.title()

                info.append({
                    "type": broker_type.value,
                    "name": name,
                    "available": is_available
                })
            except Exception as e:
                logger.error(f"Erro ao obter info do broker {broker_type}: {e}")

        return info


# Auto-register brokers when imported
def _auto_register_brokers():
    """Registra brokers automaticamente"""
    try:
        # IQ Option
        from .iqoption.iqoption_broker import IQOptionBroker
        BrokerFactory.register_broker(BrokerType.IQOPTION, IQOptionBroker)
        logger.info("IQ Option broker registrado")
    except ImportError as e:
        logger.warning(f"IQ Option broker não disponível: {e}")

    try:
        # Pocket Option
        from .pocketoption.pocketoption_broker import PocketOptionBroker
        BrokerFactory.register_broker(BrokerType.POCKETOPTION, PocketOptionBroker)
        logger.info("Pocket Option broker registrado")
    except ImportError as e:
        logger.warning(f"Pocket Option broker não disponível: {e}")

    # Futuros brokers...
    # try:
    #     from .quotex.quotex_broker import QuotexBroker
    #     BrokerFactory.register_broker(BrokerType.QUOTEX, QuotexBroker)
    # except ImportError:
    #     pass


# Registrar brokers ao importar o módulo
_auto_register_brokers()
