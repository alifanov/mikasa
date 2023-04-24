from datetime import datetime
from unittest import TestCase

from mikasa import LimitOrder, OrderType, TrailingStopLossOrder


class OrderTestCase(TestCase):
    def test_limit_order_buy(self):
        dt = datetime.utcnow()
        order = LimitOrder(type=OrderType.BUY, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(high=120, low=110))
        self.assertTrue(order.can_be_executed(high=90, low=88))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, 1)
        self.assertEqual(dbalance, -99.9)

    def test_limit_order_sell(self):
        dt = datetime.utcnow()
        order = LimitOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None)
        self.assertTrue(order.can_be_executed(high=120, low=110))
        self.assertFalse(order.can_be_executed(high=90, low=88))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, -1)
        self.assertEqual(dbalance, 99.9)

    def test_trailing_stop_loss_order_sell(self):
        order = TrailingStopLossOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None, trail_percent=0.2)
        self.assertTrue(order.can_be_executed(high=102, low=99))
        self.assertFalse(order.can_be_executed(high=99, low=89))
        self.assertEqual(order.price, 100)
        order.update_trailing_state(high=200, low=150)
        self.assertEqual(order.price, 120)
