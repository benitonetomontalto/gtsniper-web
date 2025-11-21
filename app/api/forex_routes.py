"""Forex Trading API Routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import random
from datetime import datetime, timedelta

from ..services.forex_analyzer import ForexAnalyzer
from ..services.forex_data_provider import get_forex_provider
from ..models.schemas import (
    ForexPair,
    ForexSignal,
    ForexScanConfig,
    ForexAnalysisResponse
)
from ..core.security import get_current_user_optional

router = APIRouter(prefix="/forex", tags=["Forex Trading"])

# Instância global do analisador
forex_analyzer = ForexAnalyzer()
forex_data_provider = get_forex_provider()


def generate_mock_price_data(base_price: float, periods: int = 100):
    """Gera dados de preço simulados para demonstração"""
    highs = []
    lows = []
    closes = []

    current_price = base_price
    trend = random.choice([1, -1])  # 1 = alta, -1 = baixa

    for i in range(periods):
        # Simular movimento de preço
        volatility = base_price * 0.0005  # 0.05% de volatilidade
        change = random.uniform(-volatility, volatility) + (trend * volatility * 0.3)

        current_price += change

        # Gerar OHLC
        high = current_price + random.uniform(0, volatility * 0.5)
        low = current_price - random.uniform(0, volatility * 0.5)
        close = current_price

        highs.append(high)
        lows.append(low)
        closes.append(close)

        # Mudar tendência ocasionalmente
        if random.random() < 0.1:
            trend *= -1

    return highs, lows, closes


@router.get("/pairs", response_model=List[ForexPair])
async def get_forex_pairs(
    only_major: bool = True,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Lista todos os pares de Forex disponíveis

    Args:
        only_major: Se True, retorna apenas pares principais

    Returns:
        Lista de pares Forex
    """
    return forex_analyzer.get_available_pairs(only_major=only_major)


@router.get("/analyze/{pair}", response_model=ForexAnalysisResponse)
async def analyze_forex_pair(
    pair: str,
    timeframe: str = "M15",
    min_risk_reward: float = 1.5,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analisa um par de Forex e retorna sinais de entrada

    Args:
        pair: Par de moeda (ex: EURUSD)
        timeframe: Timeframe (M5, M15, H1, H4, D1)
        min_risk_reward: Mínimo Risk:Reward ratio

    Returns:
        Análise completa com sinais
    """
    # Validar par
    if pair not in forex_analyzer.pairs_data:
        raise HTTPException(status_code=404, detail=f"Par {pair} não encontrado")

    # Buscar dados REAIS da API
    opens, highs, lows, closes = await forex_data_provider.get_ohlc_data(
        pair=pair,
        timeframe=timeframe,
        periods=100
    )

    # Analisar
    analysis = forex_analyzer.analyze_pair(
        pair=pair,
        high_data=highs,
        low_data=lows,
        close_data=closes,
        timeframe=timeframe,
        min_risk_reward=min_risk_reward
    )

    return analysis


@router.post("/scan", response_model=List[ForexAnalysisResponse])
async def scan_forex_pairs(
    config: ForexScanConfig,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Escaneia múltiplos pares de Forex em busca de sinais

    Args:
        config: Configuração do scan

    Returns:
        Lista de análises com sinais encontrados
    """
    # Determinar quais pares escanear
    if config.pairs:
        pairs_to_scan = config.pairs
    else:
        available_pairs = forex_analyzer.get_available_pairs(only_major=config.only_major_pairs)
        pairs_to_scan = [p.symbol for p in available_pairs]

    results = []

    # Preços base
    base_prices = {
        "EURUSD": 1.0850,
        "GBPUSD": 1.2650,
        "USDJPY": 149.50,
        "USDCHF": 0.8950,
        "AUDUSD": 0.6550,
        "USDCAD": 1.3650,
        "NZDUSD": 0.6050,
        "EURJPY": 162.20,
        "GBPJPY": 189.10,
        "EURGBP": 0.8580,
        "EURAUD": 1.6550,
        "GBPAUD": 1.9280,
    }

    # Escanear cada par
    for pair in pairs_to_scan:
        if pair not in forex_analyzer.pairs_data:
            continue

        # Gerar dados para cada timeframe configurado
        for timeframe in config.timeframes:
            # Buscar dados REAIS da API
            opens, highs, lows, closes = await forex_data_provider.get_ohlc_data(
                pair=pair,
                timeframe=timeframe,
                periods=100
            )

            analysis = forex_analyzer.analyze_pair(
                pair=pair,
                high_data=highs,
                low_data=lows,
                close_data=closes,
                timeframe=timeframe,
                min_risk_reward=config.min_risk_reward
            )

            # Adicionar apenas se houver sinais
            if analysis.signals:
                results.append(analysis)

    return results


@router.get("/signals/active", response_model=List[ForexSignal])
async def get_active_forex_signals(
    timeframe: Optional[str] = None,
    min_confidence: float = 60.0,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retorna sinais Forex ativos (últimas 24h)

    Args:
        timeframe: Filtrar por timeframe específico
        min_confidence: Confiança mínima do sinal

    Returns:
        Lista de sinais ativos
    """
    # Em produção, buscar de um banco de dados
    # Por enquanto, gerar alguns sinais de demonstração

    signals = []

    # Gerar alguns sinais de exemplo
    pairs_to_demo = ["EURUSD", "GBPUSD", "USDJPY"]

    base_prices = {
        "EURUSD": 1.0850,
        "GBPUSD": 1.2650,
        "USDJPY": 149.50,
    }

    for pair in pairs_to_demo:
        # Buscar dados REAIS da API
        opens, highs, lows, closes = await forex_data_provider.get_ohlc_data(
            pair=pair,
            timeframe=timeframe or "M15",
            periods=100
        )

        signal = forex_analyzer.generate_signal(
            pair=pair,
            current_price=closes[-1],
            high_data=highs,
            low_data=lows,
            close_data=closes,
            timeframe=timeframe or "M15",
            min_risk_reward=1.5
        )

        if signal and signal.confidence >= min_confidence:
            signals.append(signal)

    return signals


@router.get("/pairs/{pair}/chart")
async def get_forex_chart_data(
    pair: str,
    timeframe: str = "M15",
    periods: int = 100,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Retorna dados de gráfico para um par Forex

    Args:
        pair: Par de moeda
        timeframe: Timeframe
        periods: Número de períodos

    Returns:
        Dados OHLC para gráfico
    """
    if pair not in forex_analyzer.pairs_data:
        raise HTTPException(status_code=404, detail=f"Par {pair} não encontrado")

    # Buscar dados REAIS da API
    opens, highs, lows, closes = await forex_data_provider.get_ohlc_data(
        pair=pair,
        timeframe=timeframe,
        periods=periods
    )

    # Calcular suportes e resistências
    supports, resistances = forex_analyzer.calculate_support_resistance(closes)
    trend = forex_analyzer.detect_trend(closes)

    # Formatar dados para retorno
    chart_data = []
    start_time = datetime.now() - timedelta(minutes=periods * 15)

    for i in range(len(closes)):
        chart_data.append({
            "time": (start_time + timedelta(minutes=i * 15)).isoformat(),
            "open": closes[i-1] if i > 0 else closes[i],
            "high": highs[i],
            "low": lows[i],
            "close": closes[i],
        })

    return {
        "pair": pair,
        "timeframe": timeframe,
        "current_price": closes[-1],
        "trend": trend,
        "support_levels": supports,
        "resistance_levels": resistances,
        "chart_data": chart_data
    }
