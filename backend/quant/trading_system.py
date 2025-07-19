"""
Quantitative Trading System
Market data, strategy backtesting, and risk management
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Trade:
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    commission: float = 0.0
    
@dataclass
class Position:
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

@dataclass
class BacktestResults:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profit_factor: float
    avg_trade_duration: float
    final_portfolio_value: float
    trades: List[Trade]
    equity_curve: List[Tuple[datetime, float]]

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on market data"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: float, portfolio_value: float, risk_per_trade: float) -> float:
        """Calculate position size based on signal strength and risk management"""
        pass

class BollingerBandsStrategy(TradingStrategy):
    """Bollinger Bands mean reversion strategy"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        default_params = {
            'window': 20,
            'num_std': 2.0,
            'entry_threshold': 0.95,
            'exit_threshold': 0.5
        }
        if parameters:
            default_params.update(parameters)
        super().__init__("BollingerBands", default_params)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on Bollinger Bands"""
        df = data.copy()
        
        window = self.parameters['window']
        num_std = self.parameters['num_std']
        entry_threshold = self.parameters['entry_threshold']
        exit_threshold = self.parameters['exit_threshold']
        
        # Calculate Bollinger Bands
        df['sma'] = df['close'].rolling(window=window).mean()
        df['std'] = df['close'].rolling(window=window).std()
        df['upper_band'] = df['sma'] + (num_std * df['std'])
        df['lower_band'] = df['sma'] - (num_std * df['std'])
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        df['bb_position'] = (df['close'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
        
        # Generate signals
        df['signal'] = 0.0
        
        # Buy when price is near lower band
        df.loc[df['bb_position'] <= (1 - entry_threshold), 'signal'] = 1.0
        
        # Sell when price is near upper band
        df.loc[df['bb_position'] >= entry_threshold, 'signal'] = -1.0
        
        # Exit when price moves back towards center
        df.loc[(df['bb_position'] > exit_threshold) & (df['bb_position'] < (1 - exit_threshold)), 'signal'] = 0.0
        
        return df
    
    def calculate_position_size(self, signal: float, portfolio_value: float, risk_per_trade: float) -> float:
        """Calculate position size based on fixed percentage risk"""
        if signal == 0:
            return 0.0
        
        # Use fixed percentage of portfolio
        return abs(signal) * portfolio_value * risk_per_trade

class MomentumStrategy(TradingStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self, parameters: Dict[str, Any] = None):
        default_params = {
            'short_window': 10,
            'long_window': 30,
            'momentum_threshold': 0.02
        }
        if parameters:
            default_params.update(parameters)
        super().__init__("Momentum", default_params)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals based on momentum"""
        df = data.copy()
        
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        threshold = self.parameters['momentum_threshold']
        
        # Calculate moving averages
        df['short_ma'] = df['close'].rolling(window=short_window).mean()
        df['long_ma'] = df['close'].rolling(window=long_window).mean()
        
        # Calculate momentum
        df['momentum'] = (df['short_ma'] / df['long_ma']) - 1
        
        # Generate signals
        df['signal'] = 0.0
        df.loc[df['momentum'] > threshold, 'signal'] = 1.0
        df.loc[df['momentum'] < -threshold, 'signal'] = -1.0
        
        return df
    
    def calculate_position_size(self, signal: float, portfolio_value: float, risk_per_trade: float) -> float:
        """Calculate position size based on signal strength"""
        if signal == 0:
            return 0.0
        
        # Scale position size by signal strength
        return abs(signal) * portfolio_value * risk_per_trade

class RiskManager:
    """Risk management system for trading strategies"""
    
    def __init__(self, max_position_size: float = 0.1, max_drawdown: float = 0.2, 
                 stop_loss: float = 0.05, take_profit: float = 0.10):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
    def check_risk_limits(self, position_size: float, portfolio_value: float, 
                         current_drawdown: float) -> Tuple[bool, str]:
        """Check if trade meets risk limits"""
        
        # Check position size limit
        if abs(position_size) > self.max_position_size * portfolio_value:
            return False, f"Position size exceeds limit: {self.max_position_size}"
        
        # Check drawdown limit
        if current_drawdown > self.max_drawdown:
            return False, f"Drawdown exceeds limit: {self.max_drawdown}"
        
        return True, "Risk checks passed"
    
    def calculate_stop_loss_price(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side.lower() == 'buy':
            return entry_price * (1 - self.stop_loss)
        else:
            return entry_price * (1 + self.stop_loss)
    
    def calculate_take_profit_price(self, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        if side.lower() == 'buy':
            return entry_price * (1 + self.take_profit)
        else:
            return entry_price * (1 - self.take_profit)

class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 100000, commission_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        
    def run_backtest(self, strategy: TradingStrategy, data: pd.DataFrame, 
                    risk_manager: RiskManager = None, risk_per_trade: float = 0.02) -> BacktestResults:
        """Run backtest for a trading strategy"""
        
        if risk_manager is None:
            risk_manager = RiskManager()
        
        # Generate signals
        signals_df = strategy.generate_signals(data)
        
        # Initialize tracking variables
        portfolio_value = self.initial_capital
        position = 0.0
        avg_cost = 0.0
        trades = []
        equity_curve = []
        peak_value = self.initial_capital
        max_drawdown = 0.0
        
        for i, row in signals_df.iterrows():
            current_price = row['close']
            signal = row['signal']
            
            # Calculate current portfolio value
            portfolio_value = self.initial_capital + (position * (current_price - avg_cost))
            
            # Track equity curve
            equity_curve.append((row.name if hasattr(row.name, 'to_pydatetime') else datetime.now(), portfolio_value))
            
            # Update peak and drawdown
            peak_value = max(peak_value, portfolio_value)
            current_drawdown = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, current_drawdown)
            
            # Check if we need to change position
            target_position_value = strategy.calculate_position_size(signal, portfolio_value, risk_per_trade)
            target_position = target_position_value / current_price if current_price > 0 else 0
            
            # Check risk limits
            position_change = target_position - position
            if position_change != 0:
                risk_ok, risk_msg = risk_manager.check_risk_limits(
                    abs(position_change * current_price), portfolio_value, current_drawdown
                )
                
                if risk_ok:
                    # Execute trade
                    trade_side = 'buy' if position_change > 0 else 'sell'
                    trade_quantity = abs(position_change)
                    commission = trade_quantity * current_price * self.commission_rate
                    
                    trade = Trade(
                        symbol='ASSET',
                        side=trade_side,
                        quantity=trade_quantity,
                        price=current_price,
                        timestamp=row.name if hasattr(row.name, 'to_pydatetime') else datetime.now(),
                        commission=commission
                    )
                    trades.append(trade)
                    
                    # Update position
                    if position == 0:
                        # Opening new position
                        position = target_position
                        avg_cost = current_price
                    else:
                        # Adjusting existing position
                        if (position > 0 and position_change > 0) or (position < 0 and position_change < 0):
                            # Adding to position
                            new_avg_cost = (position * avg_cost + position_change * current_price) / (position + position_change)
                            position += position_change
                            avg_cost = new_avg_cost
                        else:
                            # Reducing or closing position
                            position += position_change
                            if abs(position) < 1e-6:  # Position effectively closed
                                position = 0
                                avg_cost = 0
        
        # Calculate final results
        final_portfolio_value = self.initial_capital + (position * (signals_df.iloc[-1]['close'] - avg_cost))
        total_return = (final_portfolio_value - self.initial_capital) / self.initial_capital
        
        # Calculate additional metrics
        returns = pd.Series([x[1] for x in equity_curve]).pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
        
        winning_trades = [t for t in trades if self._calculate_trade_pnl(t, signals_df) > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        gross_profit = sum([self._calculate_trade_pnl(t, signals_df) for t in trades if self._calculate_trade_pnl(t, signals_df) > 0])
        gross_loss = abs(sum([self._calculate_trade_pnl(t, signals_df) for t in trades if self._calculate_trade_pnl(t, signals_df) < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        return BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(trades),
            profit_factor=profit_factor,
            avg_trade_duration=0.0,  # Simplified for now
            final_portfolio_value=final_portfolio_value,
            trades=trades,
            equity_curve=equity_curve
        )
    
    def _calculate_trade_pnl(self, trade: Trade, data: pd.DataFrame) -> float:
        """Calculate P&L for a trade (simplified)"""
        # This is a simplified calculation - in reality, you'd track the exit price
        return 0.0

class MarketDataManager:
    """Manages market data ingestion and processing"""
    
    def __init__(self):
        self.data_cache = {}
    
    def generate_sample_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                           freq: str = 'D') -> pd.DataFrame:
        """Generate sample OHLCV data for testing"""
        
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Generate random walk price data
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(0.001, 0.02, len(dates))  # 0.1% daily return, 2% volatility
        
        initial_price = 100.0
        prices = [initial_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Generate OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Add some intraday volatility
            high = price * (1 + np.random.uniform(0, 0.03))
            low = price * (1 - np.random.uniform(0, 0.03))
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = np.random.randint(10000, 100000)
            
            data.append({
                'date': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        return df
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Load market data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
        except Exception as e:
            raise Exception(f"Failed to load data from {file_path}: {e}")
    
    def get_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get market data for a symbol"""
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        if cache_key not in self.data_cache:
            # For demo purposes, generate sample data
            self.data_cache[cache_key] = self.generate_sample_data(symbol, start_date, end_date)
        
        return self.data_cache[cache_key]

class QuantSystem:
    """Main quantitative trading system coordinator"""
    
    def __init__(self):
        self.data_manager = MarketDataManager()
        self.backtest_engine = BacktestEngine()
        self.strategies = {}
        self.results_history = []
    
    def register_strategy(self, name: str, strategy: TradingStrategy):
        """Register a trading strategy"""
        self.strategies[name] = strategy
    
    def run_strategy_backtest(self, strategy_name: str, symbol: str, 
                            start_date: datetime, end_date: datetime,
                            risk_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run backtest for a specific strategy"""
        
        if strategy_name not in self.strategies:
            return {"success": False, "error": f"Strategy {strategy_name} not found"}
        
        try:
            # Get market data
            data = self.data_manager.get_data(symbol, start_date, end_date)
            
            # Setup risk manager
            risk_manager = RiskManager(**(risk_params or {}))
            
            # Run backtest
            strategy = self.strategies[strategy_name]
            results = self.backtest_engine.run_backtest(strategy, data, risk_manager)
            
            # Store results
            result_dict = {
                "strategy_name": strategy_name,
                "symbol": symbol,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_return": results.total_return,
                "sharpe_ratio": results.sharpe_ratio,
                "max_drawdown": results.max_drawdown,
                "win_rate": results.win_rate,
                "total_trades": results.total_trades,
                "profit_factor": results.profit_factor,
                "final_portfolio_value": results.final_portfolio_value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results_history.append(result_dict)
            
            return {
                "success": True,
                "results": result_dict,
                "equity_curve": [(t.isoformat(), v) for t, v in results.equity_curve]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def optimize_strategy(self, strategy_name: str, symbol: str,
                         start_date: datetime, end_date: datetime,
                         param_ranges: Dict[str, List], target_metric: str = "sharpe_ratio") -> Dict[str, Any]:
        """Optimize strategy parameters"""
        
        if strategy_name not in self.strategies:
            return {"success": False, "error": f"Strategy {strategy_name} not found"}
        
        try:
            best_params = None
            best_score = -float('inf') if target_metric != 'max_drawdown' else float('inf')
            results = []
            
            # Simple grid search (in reality, you'd use more sophisticated optimization)
            param_combinations = self._generate_param_combinations(param_ranges)
            
            for params in param_combinations[:10]:  # Limit to 10 combinations for demo
                # Create strategy with new parameters
                strategy_class = type(self.strategies[strategy_name])
                test_strategy = strategy_class(params)
                
                # Run backtest
                data = self.data_manager.get_data(symbol, start_date, end_date)
                backtest_results = self.backtest_engine.run_backtest(test_strategy, data)
                
                # Evaluate score
                score = getattr(backtest_results, target_metric)
                
                if target_metric == 'max_drawdown':
                    is_better = score < best_score
                else:
                    is_better = score > best_score
                
                if is_better:
                    best_score = score
                    best_params = params
                
                results.append({
                    "parameters": params,
                    "score": score,
                    "total_return": backtest_results.total_return,
                    "sharpe_ratio": backtest_results.sharpe_ratio,
                    "max_drawdown": backtest_results.max_drawdown
                })
            
            return {
                "success": True,
                "best_parameters": best_params,
                "best_score": best_score,
                "target_metric": target_metric,
                "all_results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_param_combinations(self, param_ranges: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate parameter combinations for optimization"""
        import itertools
        
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())
        
        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))
        
        return combinations
    
    def get_strategy_list(self) -> List[str]:
        """Get list of registered strategies"""
        return list(self.strategies.keys())
    
    def get_results_history(self) -> List[Dict[str, Any]]:
        """Get historical backtest results"""
        return self.results_history