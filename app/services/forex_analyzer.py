"""
Forex Signal Analyzer - Gerador de sinais Forex com Entry, SL e TP
"""
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
import numpy as np

from ..models.schemas import ForexSignal, ForexPair, ForexAnalysisResponse


class ForexAnalyzer:
    """Analisador de sinais para Forex"""

    # Pares principais de Forex
    MAJOR_PAIRS = {
        "EURUSD": {"name": "Euro vs US Dollar", "pip_value": 0.0001},
        "GBPUSD": {"name": "British Pound vs US Dollar", "pip_value": 0.0001},
        "USDJPY": {"name": "US Dollar vs Japanese Yen", "pip_value": 0.01},
        "USDCHF": {"name": "US Dollar vs Swiss Franc", "pip_value": 0.0001},
        "AUDUSD": {"name": "Australian Dollar vs US Dollar", "pip_value": 0.0001},
        "USDCAD": {"name": "US Dollar vs Canadian Dollar", "pip_value": 0.0001},
        "NZDUSD": {"name": "New Zealand Dollar vs US Dollar", "pip_value": 0.0001},
    }

    # Pares cruzados
    CROSS_PAIRS = {
        "EURJPY": {"name": "Euro vs Japanese Yen", "pip_value": 0.01},
        "GBPJPY": {"name": "British Pound vs Japanese Yen", "pip_value": 0.01},
        "EURGBP": {"name": "Euro vs British Pound", "pip_value": 0.0001},
        "EURAUD": {"name": "Euro vs Australian Dollar", "pip_value": 0.0001},
        "GBPAUD": {"name": "British Pound vs Australian Dollar", "pip_value": 0.0001},
    }

    def __init__(self):
        self.pairs_data = {**self.MAJOR_PAIRS, **self.CROSS_PAIRS}

    def get_available_pairs(self, only_major: bool = True) -> List[ForexPair]:
        """Retorna lista de pares disponíveis"""
        pairs_dict = self.MAJOR_PAIRS if only_major else self.pairs_data

        return [
            ForexPair(
                symbol=symbol,
                name=info["name"],
                pip_value=info["pip_value"],
                is_active=True
            )
            for symbol, info in pairs_dict.items()
        ]

    def calculate_support_resistance(
        self,
        price_data: List[float],
        lookback: int = 50
    ) -> Tuple[List[float], List[float]]:
        """
        Calcula níveis de suporte e resistência

        Args:
            price_data: Lista de preços históricos
            lookback: Quantidade de períodos para análise

        Returns:
            Tuple com listas de suportes e resistências
        """
        if len(price_data) < lookback:
            lookback = len(price_data)

        recent_prices = price_data[-lookback:]

        # Identificar pontos de pivô
        supports = []
        resistances = []

        for i in range(2, len(recent_prices) - 2):
            # Suporte: mínimo local
            if (recent_prices[i] < recent_prices[i-1] and
                recent_prices[i] < recent_prices[i-2] and
                recent_prices[i] < recent_prices[i+1] and
                recent_prices[i] < recent_prices[i+2]):
                supports.append(recent_prices[i])

            # Resistência: máximo local
            if (recent_prices[i] > recent_prices[i-1] and
                recent_prices[i] > recent_prices[i-2] and
                recent_prices[i] > recent_prices[i+1] and
                recent_prices[i] > recent_prices[i+2]):
                resistances.append(recent_prices[i])

        # Remover duplicatas próximas (cluster)
        supports = self._cluster_levels(supports)
        resistances = self._cluster_levels(resistances)

        return supports[-3:] if supports else [], resistances[-3:] if resistances else []

    def _cluster_levels(self, levels: List[float], threshold: float = 0.0005) -> List[float]:
        """Agrupa níveis próximos em um único nível"""
        if not levels:
            return []

        sorted_levels = sorted(levels)
        clustered = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            if abs(level - clustered[-1]) > threshold:
                clustered.append(level)

        return clustered

    def detect_trend(self, price_data: List[float], period: int = 20) -> str:
        """
        Detecta tendência usando médias móveis simples

        Returns:
            "uptrend", "downtrend", ou "sideways"
        """
        if len(price_data) < period:
            return "sideways"

        recent = price_data[-period:]
        sma_fast = np.mean(recent[-10:])
        sma_slow = np.mean(recent)

        if sma_fast > sma_slow * 1.001:
            return "uptrend"
        elif sma_fast < sma_slow * 0.999:
            return "downtrend"
        else:
            return "sideways"

    def calculate_atr(self, high_data: List[float], low_data: List[float],
                     close_data: List[float], period: int = 14) -> float:
        """Calcula Average True Range para determinar volatilidade"""
        if len(high_data) < period + 1:
            return 0.0

        true_ranges = []
        for i in range(1, len(high_data)):
            tr = max(
                high_data[i] - low_data[i],
                abs(high_data[i] - close_data[i-1]),
                abs(low_data[i] - close_data[i-1])
            )
            true_ranges.append(tr)

        return np.mean(true_ranges[-period:]) if true_ranges else 0.0

    def generate_signal(
        self,
        pair: str,
        current_price: float,
        high_data: List[float],
        low_data: List[float],
        close_data: List[float],
        timeframe: str = "M15",
        min_risk_reward: float = 1.5
    ) -> Optional[ForexSignal]:
        """
        Gera sinal de entrada com Stop Loss e Take Profit

        Args:
            pair: Par de moeda (ex: "EURUSD")
            current_price: Preço atual
            high_data: Lista de máximas
            low_data: Lista de mínimas
            close_data: Lista de fechamentos
            timeframe: Timeframe da análise
            min_risk_reward: Mínimo Risk:Reward ratio

        Returns:
            ForexSignal ou None se não houver sinal
        """
        # Calcular suportes e resistências
        supports, resistances = self.calculate_support_resistance(close_data)

        # Se não houver suportes/resistências, criar níveis baseados no preço atual
        if not supports:
            supports = [current_price * 0.998, current_price * 0.995, current_price * 0.992]
        if not resistances:
            resistances = [current_price * 1.002, current_price * 1.005, current_price * 1.008]

        # Detectar tendência
        trend = self.detect_trend(close_data)

        # Calcular ATR para stop loss dinâmico
        atr = self.calculate_atr(high_data, low_data, close_data)
        if atr == 0:
            atr = current_price * 0.001  # 0.1% de volatilidade padrão

        pip_value = self.pairs_data.get(pair, {}).get("pip_value", 0.0001)

        # Lógica de geração de sinal - SEMPRE GERAR SINAL
        signal = None
        confluences = []

        # SINAL DE COMPRA (BUY)
        if trend == "uptrend" or trend == "sideways":
            nearest_support = min(supports, key=lambda x: abs(x - current_price))

            # Gerar sinal BUY (condição mais relaxada)
            if True:  # Sempre gerar
                entry = current_price
                stop_loss = nearest_support - (atr * 1.5)

                # Encontrar próxima resistência para Take Profit
                higher_resistances = [r for r in resistances if r > entry]
                if higher_resistances:
                    take_profit = min(higher_resistances)
                else:
                    take_profit = entry + (entry - stop_loss) * min_risk_reward

                risk = entry - stop_loss
                reward = take_profit - entry

                if risk > 0 and reward / risk >= min_risk_reward:
                    confluences = ["Uptrend", "Support Level", f"ATR: {atr:.5f}"]

                    signal = ForexSignal(
                        signal_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        pair=pair,
                        direction="BUY",
                        entry_price=entry,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        risk_reward_ratio=round(reward / risk, 2),
                        timeframe=timeframe,
                        pattern="Support Bounce",
                        confluences=confluences,
                        confidence=75.0,
                        pips_target=round((take_profit - entry) / pip_value, 1),
                        pips_stop=round((entry - stop_loss) / pip_value, 1)
                    )

        # SINAL DE VENDA (SELL)
        elif trend == "downtrend":
            nearest_resistance = min(resistances, key=lambda x: abs(x - current_price))

            # Gerar sinal SELL (condição mais relaxada)
            if True:  # Sempre gerar
                entry = current_price
                stop_loss = nearest_resistance + (atr * 1.5)

                # Encontrar próximo suporte para Take Profit
                lower_supports = [s for s in supports if s < entry]
                if lower_supports:
                    take_profit = max(lower_supports)
                else:
                    take_profit = entry - (stop_loss - entry) * min_risk_reward

                risk = stop_loss - entry
                reward = entry - take_profit

                if risk > 0 and reward / risk >= min_risk_reward:
                    confluences = ["Downtrend", "Resistance Level", f"ATR: {atr:.5f}"]

                    signal = ForexSignal(
                        signal_id=str(uuid.uuid4()),
                        timestamp=datetime.now(),
                        pair=pair,
                        direction="SELL",
                        entry_price=entry,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        risk_reward_ratio=round(reward / risk, 2),
                        timeframe=timeframe,
                        pattern="Resistance Rejection",
                        confluences=confluences,
                        confidence=75.0,
                        pips_target=round((entry - take_profit) / pip_value, 1),
                        pips_stop=round((stop_loss - entry) / pip_value, 1)
                    )

        return signal

    def analyze_pair(
        self,
        pair: str,
        high_data: List[float],
        low_data: List[float],
        close_data: List[float],
        timeframe: str = "M15",
        min_risk_reward: float = 1.5
    ) -> ForexAnalysisResponse:
        """
        Análise completa de um par Forex

        Returns:
            ForexAnalysisResponse com análise e sinais
        """
        current_price = close_data[-1] if close_data else 0.0

        # Calcular suportes e resistências
        supports, resistances = self.calculate_support_resistance(close_data)

        # Detectar tendência
        trend = self.detect_trend(close_data)

        # Gerar sinal se houver oportunidade
        signals = []
        signal = self.generate_signal(
            pair, current_price, high_data, low_data, close_data,
            timeframe, min_risk_reward
        )
        if signal:
            signals.append(signal)

        # Recomendação
        recommendation = None
        if trend == "uptrend" and signals:
            recommendation = f"Aguardar pullback para {supports[0]:.5f} para entrada BUY"
        elif trend == "downtrend" and signals:
            recommendation = f"Aguardar rejeição em {resistances[0]:.5f} para entrada SELL"
        else:
            recommendation = "Sem setup claro no momento. Aguardar."

        return ForexAnalysisResponse(
            pair=pair,
            current_price=current_price,
            trend=trend,
            support_levels=supports,
            resistance_levels=resistances,
            recommendation=recommendation,
            signals=signals
        )
