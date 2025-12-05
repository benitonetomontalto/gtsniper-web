"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# Authentication
class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = None  # Senha opcional
    access_token: Optional[str] = None

    # Broker selection (new multi-broker support)
    broker_type: Optional[str] = Field(default="iqoption", description="Broker type: iqoption or pocketoption")

    # IQ Option credentials
    iqoption_email: Optional[str] = None
    iqoption_password: Optional[str] = None
    iqoption_account_type: Optional[str] = None

    # Pocket Option credentials
    pocketoption_ssid: Optional[str] = None
    pocketoption_account_type: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    access_message: Optional[str] = None
    access_token_label: Optional[str] = None

    # Broker connection info (generic)
    broker_type: Optional[str] = None
    broker_connected: Optional[bool] = None
    broker_message: Optional[str] = None
    broker_balance: Optional[float] = None
    broker_account_type: Optional[str] = None

    # Backward compatibility (deprecated - use broker_* fields)
    iq_option_connected: Optional[bool] = None
    iq_option_message: Optional[str] = None
    iq_option_balance: Optional[float] = None
    iq_option_account_type: Optional[str] = None
    iq_option_two_factor_required: Optional[bool] = None
    iq_option_two_factor_message: Optional[str] = None


# Trading Pair
class TradingPair(BaseModel):
    symbol: str
    name: str
    is_otc: bool = False
    is_active: bool = True
    market_type: Optional[str] = None


# Candle Data
class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# Price Action Pattern
class PriceActionPattern(BaseModel):
    pattern_type: Literal[
        "pin_bar",
        "engulfing_bullish",
        "engulfing_bearish",
        "inside_bar",
        "doji",
        "bos_bullish",
        "bos_bearish"
    ]
    description: str
    candle_index: int


# Support/Resistance Level
class SupportResistanceLevel(BaseModel):
    level: float
    type: Literal["support", "resistance"]
    strength: int = Field(ge=1, le=5)
    touches: int


# Trading Signal
class TradingSignal(BaseModel):
    signal_id: str
    timestamp: datetime  # Quando o sinal foi gerado
    symbol: str
    timeframe: int
    direction: Literal["CALL", "PUT"]
    entry_price: float
    entry_time: Optional[datetime] = None  # Horário de entrada (futuro - próxima vela)
    expiry_time: Optional[datetime] = None  # Horário de expiração
    pattern: PriceActionPattern
    support_resistance: Optional[SupportResistanceLevel] = None
    confluences: List[str] = []
    confidence: float = Field(ge=0, le=100)
    expiry_minutes: int = 5


# Scan Configuration
class ScanConfig(BaseModel):
    mode: Literal["manual", "auto"] = "auto"
    symbols: Optional[List[str]] = None
    timeframe: int = Field(default=5, description="Primary timeframe in minutes")
    timeframes: Optional[List[int]] = None  # Lista de timeframes para escanear (se None, usa só timeframe)
    sensitivity: Literal["conservative", "moderate", "aggressive"] = "moderate"
    use_volume_filter: bool = True
    use_volatility_filter: bool = True
    use_trend_filter: bool = True
    only_otc: bool = False
    only_open_market: bool = False  # Filter for open market only (not OTC)

    @field_validator('timeframe')
    @classmethod
    def validate_timeframe(cls, v: int) -> int:
        """Validate that timeframe is a valid IQ Option timeframe"""
        valid_timeframes = [1, 5, 15, 30, 60]
        if v not in valid_timeframes:
            raise ValueError(f"Timeframe must be one of {valid_timeframes}, got {v}")
        return v

    @field_validator('timeframes')
    @classmethod
    def validate_timeframes(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate that all timeframes are valid"""
        if v is None:
            return v

        valid_timeframes = {1, 5, 15, 30, 60}
        invalid = [tf for tf in v if tf not in valid_timeframes]
        if invalid:
            raise ValueError(f"Invalid timeframes: {invalid}. Must be one of {valid_timeframes}")

        return v

    @model_validator(mode='after')
    def validate_market_filters(self):
        """Validate that only_otc and only_open_market are not both True"""
        if self.only_otc and self.only_open_market:
            raise ValueError("Cannot set both only_otc and only_open_market to True")
        return self

    @model_validator(mode='after')
    def sync_timeframes(self):
        """Ensure primary timeframe is in timeframes list"""
        if self.timeframes is None:
            self.timeframes = [self.timeframe]
        elif self.timeframe not in self.timeframes:
            # Add primary timeframe to list if missing
            self.timeframes = [self.timeframe] + self.timeframes
        return self


# Statistics
class TradingStats(BaseModel):
    total_signals: int
    win_signals: int
    loss_signals: int
    winrate: float
    best_pairs: List[dict]
    average_response_time: float


# Alert Configuration
class AlertConfig(BaseModel):
    sound_enabled: bool = True
    visual_enabled: bool = True
    telegram_enabled: bool = False
    pre_signal_alert: bool = False


# User Settings
class UserSettings(BaseModel):
    scan_config: ScanConfig
    alert_config: AlertConfig
    mboption_token: Optional[str] = None


# Signal Response (detailed)
class SignalResponse(BaseModel):
    signal: TradingSignal
    chart_data: List[Candle]
    indicators: dict
    explanation: str


# ============================================================================
# FOREX MODELS
# ============================================================================

# Forex Trading Signal (com Stop Loss e Take Profit)
class ForexSignal(BaseModel):
    signal_id: str
    timestamp: datetime
    pair: str  # Ex: "EURUSD", "GBPUSD"
    direction: Literal["BUY", "SELL"]
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float  # Ex: 1:2, 1:3
    timeframe: str  # Ex: "M5", "M15", "H1", "H4"
    pattern: Optional[str] = None  # Ex: "Breakout", "Reversal", "Trend"
    confluences: List[str] = []  # Confluências (suporte/resistência, médias, etc)
    confidence: float = Field(ge=0, le=100)
    pips_target: float  # Quantidade de pips esperados
    pips_stop: float  # Quantidade de pips do stop loss


# Forex Pair Info
class ForexPair(BaseModel):
    symbol: str  # Ex: "EURUSD"
    name: str  # Ex: "Euro vs US Dollar"
    is_active: bool = True
    pip_value: float = 0.0001  # Valor de 1 pip
    spread: Optional[float] = None  # Spread atual


# Forex Scan Configuration
class ForexScanConfig(BaseModel):
    pairs: Optional[List[str]] = None  # Pares específicos ou todos
    timeframes: List[str] = ["M5", "M15", "H1"]  # Timeframes para análise
    min_risk_reward: float = Field(default=1.5, ge=1.0)  # Mínimo R:R
    use_trend_filter: bool = True
    use_support_resistance: bool = True
    only_major_pairs: bool = True  # Apenas pares principais (EUR, GBP, USD, etc)


# Forex Analysis Response
class ForexAnalysisResponse(BaseModel):
    pair: str
    current_price: float
    trend: str  # "uptrend", "downtrend", "sideways"
    support_levels: List[float]
    resistance_levels: List[float]
    recommendation: Optional[str] = None
    signals: List[ForexSignal]


# ============================================================================
# BROKER MODELS (Multi-Broker Support)
# ============================================================================

# Available Broker Info
class BrokerInfo(BaseModel):
    broker_type: str  # "iqoption", "pocketoption"
    name: str  # "IQ Option", "Pocket Option"
    available: bool  # Se biblioteca está disponível
    auth_type: str  # "email_password" ou "ssid"
    description: Optional[str] = None


# List of Available Brokers Response
class AvailableBrokersResponse(BaseModel):
    brokers: List[BrokerInfo]
