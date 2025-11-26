"""
Trading Signal Generator
Combines Price Action, Indicators, and S/R levels to generate trading signals
"""
import pandas as pd
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from ...models.schemas import (
    TradingSignal,
    PriceActionPattern,
    SupportResistanceLevel,
    ScanConfig
)
from ..price_action.pattern_detector import PriceActionDetector
from ..price_action.support_resistance import SupportResistanceDetector
from ..indicators.technical_indicators import TechnicalIndicators


class SignalGenerator:
    """Generate trading signals based on multiple confluences"""

    def __init__(self, config: ScanConfig):
        """
        Initialize signal generator

        Args:
            config: Scan configuration
        """
        self.config = config
        self.pattern_detector = PriceActionDetector(sensitivity=config.sensitivity)
        self.sr_detector = SupportResistanceDetector()
        self.indicators = TechnicalIndicators()

        # LOG das configurações aplicadas
        print(f"[SignalGenerator] Configuração aplicada:")
        print(f"  - Sensibilidade: {config.sensitivity}")
        print(f"  - Timeframe: {config.timeframe}M")
        print(f"  - Somente OTC: {config.only_otc}")
        print(f"  - Somente Mercado Aberto: {config.only_open_market}")

    def generate_signal(
        self,
        symbol: str,
        df: pd.DataFrame
    ) -> Optional[TradingSignal]:
        """
        Generate trading signal for a symbol - 100% REAL, SEM SINAIS SIMULADOS

        Args:
            symbol: Trading pair symbol
            df: DataFrame with OHLC data

        Returns:
            TradingSignal if valid signal found, None otherwise
        """
        # VALIDAÇÃO RIGOROSA: Mínimo de candles SEMPRE
        min_candles = 50  # SEMPRE exige 50 candles para análise confiável
        if len(df) < min_candles:
            print(f"[SignalGenerator] {symbol}: Candles insuficientes ({len(df)}/{min_candles}) - IGNORADO")
            return None

        # Detect patterns - APENAS PADRÕES REAIS
        patterns = self.pattern_detector.detect_patterns(df)

        # SEM PADRÕES REAIS = SEM SINAL (NUNCA INVENTAR!)
        if not patterns:
            return None

        # Get the most recent pattern
        pattern = patterns[-1]

        # Detect support/resistance levels
        sr_levels = self.sr_detector.detect_levels(df)

        # Get current price
        current_price = df['close'].iloc[-1]

        # Check if near S/R level
        is_near, sr_level = self.sr_detector.is_near_level(current_price, sr_levels)

        # Determine signal direction - APENAS SE HOUVER DIREÇÃO CLARA
        direction = self._determine_direction(pattern, sr_level, df)

        # SEM DIREÇÃO CLARA = SEM SINAL (NUNCA ADIVINHAR!)
        if not direction:
            print(f"[SignalGenerator] {symbol}: Direção não determinada - IGNORADO")
            return None

        # Apply filters - SEMPRE OBRIGATÓRIO
        filters_ok = self._apply_filters(df, direction)

        # FILTROS FALHARAM = SEM SINAL (SEM EXCEÇÕES!)
        if not filters_ok:
            print(f"[SignalGenerator] {symbol}: Filtros não aprovados - IGNORADO")
            return None

        # Calculate confluences - MÍNIMO 2 CONFLUÊNCIAS REAIS
        confluences = self._calculate_confluences(pattern, sr_level, df, direction)

        # SEM CONFLUÊNCIAS SUFICIENTES = SEM SINAL
        min_confluences = 3 if self.config.sensitivity == "conservative" else 2
        if len(confluences) < min_confluences:
            print(f"[SignalGenerator] {symbol}: Confluências insuficientes ({len(confluences)}/{min_confluences}) - IGNORADO")
            return None

        # Calculate confidence - BASEADO APENAS EM CONFLUÊNCIAS REAIS
        confidence = self._calculate_confidence(confluences, pattern, sr_level)

        # Calculate entry and expiry times (FUTURO!) - usando horário de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(brasilia_tz)

        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        entry_buffer = 1 if self.config.sensitivity == "aggressive" else 0
        entry_time = next_minute + timedelta(minutes=entry_buffer)

        expiry_minutes = max(self.config.timeframe, 2)
        expiry_time = entry_time + timedelta(minutes=expiry_minutes)

        # Generate signal
        signal = TradingSignal(
            signal_id=str(uuid.uuid4()),
            timestamp=now,  # Quando foi gerado
            symbol=symbol,
            timeframe=self.config.timeframe,
            direction=direction,
            entry_price=current_price,
            entry_time=entry_time,  # Quando entrar (futuro)
            expiry_time=expiry_time,  # Quando expira
            pattern=pattern.model_dump() if pattern else None,
            support_resistance=sr_level.model_dump() if (sr_level and is_near) else None,
            confluences=confluences,
            confidence=confidence,
            expiry_minutes=expiry_minutes
        )

        return signal

    def _determine_direction(
        self,
        pattern: PriceActionPattern,
        sr_level: Optional[SupportResistanceLevel],
        df: pd.DataFrame
    ) -> Optional[str]:
        """
        Determine signal direction (CALL or PUT) - 100% BASEADO EM ANÁLISE REAL

        Retorna None se não houver direção clara - NUNCA inventa!
        """

        # Padrões claramente bullish
        if pattern.pattern_type in ["pin_bar", "engulfing_bullish", "bos_bullish"]:
            return "CALL"

        # Padrões claramente bearish
        if pattern.pattern_type in ["engulfing_bearish", "bos_bearish"]:
            return "PUT"

        # Doji - usar RSI para decidir APENAS se RSI estiver em zona extrema
        if pattern.pattern_type == "doji":
            rsi = self.indicators.calculate_rsi(df)
            if len(rsi) > 0:
                rsi_value = rsi.iloc[-1]
                # APENAS zonas extremas
                if rsi_value < 30:  # Sobrevenda clara
                    return "CALL"
                elif rsi_value > 70:  # Sobrecompra clara
                    return "PUT"
            # RSI não extremo = sem direção clara
            return None

        # Inside bar - usar tendência APENAS se for forte
        if pattern.pattern_type == "inside_bar":
            trend = self.indicators.detect_trend(df)
            if trend == "bullish":
                return "CALL"
            elif trend == "bearish":
                return "PUT"
            # Sem tendência clara = sem direção
            return None

        # Padrão não reconhecido = SEM SINAL
        return None

    def _apply_filters(self, df: pd.DataFrame, direction: str) -> bool:
        """
        Apply various filters based on configuration - SEMPRE RIGOROSO

        Todos os modos aplicam filtros reais, apenas com níveis diferentes
        """
        trend = self.indicators.detect_trend(df)

        # MODO AGRESSIVO: Filtros básicos mas REAIS
        if self.config.sensitivity == "aggressive":
            # Evita contra-tendência forte
            if direction == "CALL" and trend == "bearish":
                return False
            if direction == "PUT" and trend == "bullish":
                return False

            # Evita volatilidade extrema (mercado errático)
            if self.indicators.is_high_volatility(df, threshold=4.0):
                return False

            return True

        # MODO MODERADO: Filtros intermediários
        if self.config.sensitivity == "moderate":
            # Trend filter (evita contra-tendência)
            if direction == "CALL" and trend == "bearish":
                return False
            if direction == "PUT" and trend == "bullish":
                return False

            # Volatility filter
            if self.indicators.is_high_volatility(df, threshold=2.5):
                return False

            # Volume deve estar pelo menos normal (não decrescente)
            if self.indicators.is_volume_decreasing(df):
                return False

            return True

        # MODO CONSERVADOR: Filtros MUITO RIGOROSOS
        if self.config.sensitivity == "conservative":
            # Volume filter (OBRIGATÓRIO - deve estar crescente)
            if not self.indicators.is_volume_increasing(df):
                return False

            # Volatility filter (rigoroso)
            if self.indicators.is_high_volatility(df, threshold=2.0):
                return False

            # Trend filter (OBRIGATÓRIO - deve estar ALINHADO)
            if direction == "CALL" and trend != "bullish":
                return False
            if direction == "PUT" and trend != "bearish":
                return False

            return True

        return True

    def _calculate_confluences(
        self,
        pattern: PriceActionPattern,
        sr_level: Optional[SupportResistanceLevel],
        df: pd.DataFrame,
        direction: str
    ) -> List[str]:
        """Calculate all confluences supporting the signal"""
        confluences = []

        # Pattern confluence
        confluences.append(f"Padro: {pattern.description}")

        # Support/Resistance confluence
        if sr_level:
            confluences.append(
                f"{sr_level.type.capitalize()} em {sr_level.level:.5f} "
                f"(Fora: {sr_level.strength}/5)"
            )

        # Trend confluence
        trend = self.indicators.detect_trend(df)
        if (direction == "CALL" and trend == "bullish") or \
           (direction == "PUT" and trend == "bearish"):
            confluences.append(f"Tendncia {trend} favorvel")

        # Volume confluence
        if self.indicators.is_volume_increasing(df):
            confluences.append("Volume crescente confirmando movimento")

        # RSI confluence - APENAS ZONAS EXTREMAS REAIS
        rsi = self.indicators.calculate_rsi(df)
        if len(rsi) > 0:
            rsi_value = rsi.iloc[-1]
            # Sobrevenda: RSI < 30 (não 40!)
            if direction == "CALL" and rsi_value < 30:
                confluences.append(f"RSI em sobrevenda extrema ({rsi_value:.1f})")
            # Sobrecompra: RSI > 70 (não 60!)
            elif direction == "PUT" and rsi_value > 70:
                confluences.append(f"RSI em sobrecompra extrema ({rsi_value:.1f})")

        # MACD confluence
        macd_line, signal_line, _ = self.indicators.calculate_macd(df)
        if len(macd_line) > 1 and len(signal_line) > 1:
            if direction == "CALL" and macd_line.iloc[-1] > signal_line.iloc[-1]:
                confluences.append("MACD bullish")
            elif direction == "PUT" and macd_line.iloc[-1] < signal_line.iloc[-1]:
                confluences.append("MACD bearish")

        # Moving Average Crossover (MA 9 x MA 21) confluence
        ma_cross = self.indicators.check_ma_crossover(df, fast_period=9, slow_period=21)
        if ma_cross == 'bullish_cross' and direction == "CALL":
            confluences.append("Cruzamento MA9 x MA21 (ALTA)")
        elif ma_cross == 'bearish_cross' and direction == "PUT":
            confluences.append("Cruzamento MA9 x MA21 (BAIXA)")
        elif ma_cross == 'bullish_aligned' and direction == "CALL":
            confluences.append("MA9 > MA21 (tendência de alta)")
        elif ma_cross == 'bearish_aligned' and direction == "PUT":
            confluences.append("MA9 < MA21 (tendência de baixa)")

        # Stochastic Oscillator confluence
        k_line, d_line = self.indicators.calculate_stochastic(df, k_period=14, d_period=3)
        if len(k_line) > 1 and len(d_line) > 1:
            k_value = k_line.iloc[-1]
            d_value = d_line.iloc[-1]

            # Oversold zone (< 20) - good for CALL
            if direction == "CALL" and k_value < 20 and d_value < 20:
                confluences.append(f"Estocástico em sobrevenda ({k_value:.1f})")
            # Overbought zone (> 80) - good for PUT
            elif direction == "PUT" and k_value > 80 and d_value > 80:
                confluences.append(f"Estocástico em sobrecompra ({k_value:.1f})")
            # Bullish crossover in oversold zone
            elif direction == "CALL" and k_value > d_value and k_value < 30:
                confluences.append(f"Estocástico cruzando para cima ({k_value:.1f})")
            # Bearish crossover in overbought zone
            elif direction == "PUT" and k_value < d_value and k_value > 70:
                confluences.append(f"Estocástico cruzando para baixo ({k_value:.1f})")

        return confluences

    def _calculate_confidence(
        self,
        confluences: List[str],
        pattern: PriceActionPattern,
        sr_level: Optional[SupportResistanceLevel]
    ) -> float:
        """
        Calculate signal confidence (0-100) - REALISTA

        Base baixa, apenas confluências REAIS aumentam confiança
        """
        # Base REALISTA: 30% (não 50%!)
        confidence = 30.0

        # Cada confluência REAL adiciona menos (3% em vez de 5%)
        confidence += len(confluences) * 3

        # Padrões fortes adicionam confiança
        if pattern.pattern_type in ["engulfing_bullish", "engulfing_bearish"]:
            confidence += 12
        elif pattern.pattern_type in ["bos_bullish", "bos_bearish"]:
            confidence += 8
        elif pattern.pattern_type in ["pin_bar"]:
            confidence += 10

        # S/R forte adiciona confiança
        if sr_level:
            confidence += sr_level.strength * 2

        # Limitar entre 35% e 85% (NUNCA 95%!)
        confidence = max(confidence, 35.0)  # Mínimo realista
        confidence = min(confidence, 85.0)  # Máximo realista

        return confidence
