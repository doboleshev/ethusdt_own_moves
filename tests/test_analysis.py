import math

from eth_own_moves.analysis import RollingRegression, RollingSum, cumulative_return, log_return


def test_log_return_basic():
    assert log_return(100.0, 110.0) == math.log(1.1)


def test_cumulative_return_roundtrip():
    total = math.log(1.05)
    assert abs(cumulative_return(total) - 0.05) < 1e-12


def test_rolling_regression_beta():
    reg = RollingRegression(maxlen=5)
    reg.add(1.0, 2.0)
    reg.add(2.0, 4.0)
    reg.add(3.0, 6.0)
    stats = reg.stats()
    assert abs(stats.beta - 2.0) < 1e-9


def test_rolling_sum_window():
    window = RollingSum(maxlen=3)
    window.add(0.1)
    window.add(0.2)
    window.add(0.3)
    assert abs(window.total - 0.6) < 1e-12
    window.add(0.4)
    assert abs(window.total - 0.9) < 1e-12

