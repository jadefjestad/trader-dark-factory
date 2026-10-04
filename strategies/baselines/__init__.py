"""Fixed baseline strategies. PROTECTED: these are the yardsticks candidates must beat."""
from strategies.baselines.buy_hold import EqualWeightBuyHold
from strategies.baselines.sma_trend import SmaTrend
from strategies.baselines.momentum import CrossSectionalMomentum
from strategies.baselines.mean_reversion import ShortTermReversal
from strategies.baselines.intraday_orb import OpeningRangeBreakout

DAILY = [EqualWeightBuyHold, SmaTrend, CrossSectionalMomentum, ShortTermReversal]
INTRADAY = [OpeningRangeBreakout]
ALL = DAILY + INTRADAY
