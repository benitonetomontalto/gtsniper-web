"""IQ Option Scanner - Scans OTC pairs using IQ Option data"""
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd

from ...models.schemas import ScanConfig, TradingSignal
from ..iqoption import get_session_manager
from .signal_generator import SignalGenerator


class IQOptionScanner:
    """Scanner that uses IQ Option data for signal generation"""

    def __init__(self, username: str, config: ScanConfig):
        """
        Initialize IQ Option scanner

        Args:
            username: User to get IQ Option connection for
            config: Scanner configuration
        """
        self.username = username
        self.config = config
        self.signal_generator = SignalGenerator(config)
        self.is_running = False
        self.latest_signals: Dict[str, TradingSignal] = {}
        self.session_manager = get_session_manager()
        self._scan_task: Optional[asyncio.Task] = None
        # CRITICAL: Limit concurrent requests to prevent memory explosion
        self._semaphore = asyncio.Semaphore(5)  # Max 5 concurrent pair scans
        self._scan_interval = 30  # Scan every 30 seconds (more stable)

    async def start_scanning(self):
        """Start scanning IQ Option OTC pairs"""
        self.is_running = True

        print(f"[IQOptionScanner] ========================================")
        print(f"[IQOptionScanner] INICIANDO SCAN")
        print(f"[IQOptionScanner] Usuario: {self.username}")
        print(f"[IQOptionScanner] Timeframe configurado: {self.config.timeframe} minutos")
        print(f"[IQOptionScanner] Timeframe em segundos: {self.config.timeframe * 60}")
        print(f"[IQOptionScanner] ========================================")

        # Check if user is connected
        is_connected = self.session_manager.is_connected(self.username)
        print(f"[IQOptionScanner] Verificando conexao: is_connected={is_connected}")

        if not is_connected:
            print(f"[IQOptionScanner] ERRO: Usuario {self.username} nao conectado ao IQ Option")
            print(f"[IQOptionScanner] Scanner nao pode iniciar sem conexao ativa")
            self.is_running = False
            return

        # Refresh session timeout
        client = self.session_manager.get_client(self.username)
        if client:
            print(f"[IQOptionScanner] Conexao OK - Cliente ativo: {client.is_connected}")
            print(f"[IQOptionScanner] Timeout da sessao atualizado")
        else:
            print(f"[IQOptionScanner] AVISO: Cliente nao encontrado no session_manager")
            self.is_running = False
            return

        # Get trading pairs (OTC or regular based on config)
        pairs = await self._get_trading_pairs()

        if not pairs:
            print("[IQOptionScanner] Nenhum par disponível para escanear")
            self.is_running = False
            return

        # Determinar quais timeframes usar - RETROCOMPATIBILIDADE
        # Se timeframes for None ou lista vazia, usa timeframe primário
        if self.config.timeframes and len(self.config.timeframes) > 0:
            timeframes_to_scan = self.config.timeframes
            print(f"[IQOptionScanner] Usando MULTIPLOS timeframes: {timeframes_to_scan}")
        else:
            timeframes_to_scan = [self.config.timeframe]
            print(f"[IQOptionScanner] Usando timeframe UNICO (fallback): {timeframes_to_scan}")

        print(f"[IQOptionScanner] Iniciando scan em {len(pairs)} pares OTC")
        print(f"[IQOptionScanner] Timeframes a escanear: {timeframes_to_scan} minutos")

        while self.is_running:
            try:
                # Verify connection is still active before scanning
                if not self.session_manager.is_connected(self.username):
                    print(f"[IQOptionScanner] ERRO: Conexao perdida durante scan!")
                    print(f"[IQOptionScanner] Parando scanner - reconecte e tente novamente")
                    self.is_running = False
                    break

                # Scan all OTC pairs with controlled concurrency
                # CRITICAL FIX: Process pairs in batches to prevent memory explosion
                new_signals = []
                for pair in pairs:
                    if not self.is_running:
                        break

                    # Escanear cada timeframe configurado
                    for timeframe in timeframes_to_scan:
                        if not self.is_running:
                            break

                        async with self._semaphore:
                            try:
                                # Add timeout to prevent hanging requests
                                result = await asyncio.wait_for(
                                    self._scan_pair(pair, timeframe),
                                    timeout=10.0  # 10 second timeout per pair
                                )
                                if isinstance(result, TradingSignal):
                                    new_signals.append(result)
                                    # Usar chave única: símbolo + timeframe
                                    signal_key = f"{result.symbol}_{result.timeframe}M"
                                    self.latest_signals[signal_key] = result
                            except asyncio.TimeoutError:
                                print(f"[IQOptionScanner] Timeout ao escanear {pair.get('symbol', '?')} {timeframe}M")
                            except Exception as e:
                                print(f"[IQOptionScanner] Erro ao escanear {pair.get('symbol', '?')} {timeframe}M: {e}")

                # Log new signals
                if new_signals:
                    print(f"[IQOptionScanner] {len(new_signals)} novos sinais OTC!")
                    for signal in new_signals:
                        print(f"  - {signal.symbol}: {signal.direction} "
                              f"({signal.confidence:.1f}% confianca)")

                # Wait before next scan (increased for stability)
                await asyncio.sleep(self._scan_interval)

            except asyncio.CancelledError:
                print(f"[IQOptionScanner] Scan cancelado via stop_scanning()")
                break
            except Exception as e:
                print(f"[IQOptionScanner] Erro durante scan: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)

    def stop_scanning(self):
        """Stop scanning and clean up state"""
        self.is_running = False

        # Cancel the scanning task if it exists
        if self._scan_task and not self._scan_task.done():
            self._scan_task.cancel()
            print("[IQOptionScanner] Task de scan cancelada")

        # Clear latest signals to ensure fresh start on resume
        self.latest_signals.clear()

        print("[IQOptionScanner] Scan interrompido e estado limpo")

    async def _get_trading_pairs(self) -> List[Dict]:
        """Get available trading pairs from IQ Option (OTC or regular) honoring scanner config"""
        try:
            # Determine include_otc flag based on scanner configuration
            # If only_open_market=True, we want include_otc=False (exclude OTC)
            # If only_otc=True, we want include_otc=True (include OTC)
            # Otherwise, include both (include_otc=True by default)
            include_otc_flag = not self.config.only_open_market
            print(f"[IQOptionScanner] Solicitando pares com include_otc={include_otc_flag}")

            pairs = await self.session_manager.get_user_pairs(self.username, include_otc=include_otc_flag)
            print(f"[IQOptionScanner] Total de pares recebidos da IQ Option: {len(pairs)}")

            # Filter only active pairs
            active_pairs = [p for p in pairs if p.get("is_active", False)]
            print(f"[IQOptionScanner] Pares ativos: {len(active_pairs)}")

            # Count OTC vs non-OTC before filtering
            otc_count = sum(1 for p in active_pairs if p.get("is_otc", False))
            non_otc_count = len(active_pairs) - otc_count
            print(f"[IQOptionScanner] Distribuição: {otc_count} OTC, {non_otc_count} Mercado Regular")

            # Respect scanner configuration filters
            if self.config.only_otc:
                active_pairs = [p for p in active_pairs if p.get("is_otc", False)]
                print(f"[IQOptionScanner] Filtro ONLY_OTC aplicado: {len(active_pairs)} pares")
            elif self.config.only_open_market:
                active_pairs = [p for p in active_pairs if not p.get("is_otc", False)]
                print(f"[IQOptionScanner] Filtro ONLY_OPEN_MARKET aplicado: {len(active_pairs)} pares")
            else:
                print(f"[IQOptionScanner] SEM filtro de mercado: {len(active_pairs)} pares (OTC + Regular)")

            if self.config.symbols:
                symbols_set = {symbol.upper() for symbol in self.config.symbols}
                active_pairs = [
                    p for p in active_pairs
                    if p.get("symbol", "").upper() in symbols_set
                ]
                print(f"[IQOptionScanner] Filtro de símbolos aplicado: {len(active_pairs)} pares")

            # Log alguns exemplos dos pares filtrados
            if active_pairs:
                sample_pairs = active_pairs[:10]  # Mostrar mais exemplos
                print(f"[IQOptionScanner] Exemplos de pares a escanear:")
                for p in sample_pairs:
                    otc_label = "OTC" if p.get('is_otc', False) else "REGULAR"
                    market_type = p.get('type', '?')
                    print(f"  - {p.get('symbol')} ({otc_label}, Tipo: {market_type})")

            return active_pairs

        except Exception as e:
            print(f"[IQOptionScanner] Erro ao buscar pares: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _scan_pair(self, pair: Dict, timeframe: int) -> Optional[TradingSignal]:
        """
        Scan a single OTC pair for signals

        Args:
            pair: Trading pair info
            timeframe: Timeframe in minutes to scan

        Returns:
            Trading signal if found
        """
        try:
            symbol = pair["symbol"]

            # Get candles from IQ Option
            # Convert timeframe from minutes to seconds for IQ Option
            timeframe_seconds = timeframe * 60

            print(f"[IQOptionScanner] Buscando candles para {symbol}: timeframe={timeframe}min ({timeframe_seconds}s)")

            candles = await self.session_manager.get_user_candles(
                username=self.username,
                symbol=symbol,
                timeframe=timeframe_seconds,
                count=100  # Get 100 candles for analysis
            )

            if candles is None or candles.empty:
                print(f"[IQOptionScanner] Nenhum candle retornado para {symbol}")
                return None

            # Ensure we have a DataFrame for the generator
            if not isinstance(candles, pd.DataFrame):
                candles = pd.DataFrame(candles)

            # Validar dados dos candles
            if candles.empty or len(candles) < 5:
                print(f"[IQOptionScanner] ❌ CANDLES INSUFICIENTES: {symbol} {timeframe}M - Recebidos: {len(candles)} candles (mínimo: 5)")
                print(f"[IQOptionScanner]    → Possível causa: Par INATIVO ou SEM dados históricos")
                return None

            # Validar colunas necessárias
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in candles.columns]
            if missing_columns:
                print(f"[IQOptionScanner] ❌ CANDLES INVÁLIDOS: {symbol} - Faltam colunas: {missing_columns}")
                return None

            # Log SUCCESS - candles válidos recebidos
            print(f"[IQOptionScanner] ✅ CANDLES OK: {symbol} {timeframe}M - {len(candles)} candles recebidos")

            # Generate signal using signal generator (synchronous)
            # Criar uma config temporária com o timeframe específico
            from copy import copy
            temp_config = copy(self.config)
            temp_config.timeframe = timeframe

            # Criar signal generator temporário com timeframe correto
            from .signal_generator import SignalGenerator
            temp_generator = SignalGenerator(temp_config)
            signal = temp_generator.generate_signal(symbol, candles)

            if signal:
                print(f"[IQOptionScanner] 🎯 SINAL GERADO: {symbol} {timeframe}M - {signal.direction} ({signal.confidence:.1f}%)")
            else:
                print(f"[IQOptionScanner] ⚠️  SEM SINAL: {symbol} {timeframe}M - Nenhum padrão/confluência detectado")

            return signal

        except Exception as e:
            print(f"[IQOptionScanner] ERRO ao analisar {pair.get('symbol', '?')} {timeframe}M: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()  # Log completo do erro
            return None

    def get_latest_signals(self) -> List[TradingSignal]:
        """Get latest signals from all pairs"""
        return list(self.latest_signals.values())

    def get_status(self) -> dict:
        """Get scanner status"""
        return {
            "is_running": self.is_running,
            "username": self.username,
            "active_pairs": list(self.latest_signals.keys()),
            "signals_generated": len(self.latest_signals),
            "config": {
                "timeframe": self.config.timeframe,
                "sensitivity": self.config.sensitivity,
            }
        }
