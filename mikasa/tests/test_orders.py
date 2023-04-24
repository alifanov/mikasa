from unittest import TestCase

from mikasa import LimitOrder, OrderType


class OrderTestCase(TestCase):
    def test_limit_order_buy(self):
        order = LimitOrder(type=OrderType.BUY, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(high=120, low=110))
        self.assertTrue(order.can_be_executed(high=90, low=88))

    def test_limit_order_sell(self):
        order = LimitOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None)
        self.assertTrue(order.can_be_executed(high=120, low=110))
        self.assertFalse(order.can_be_executed(high=90, low=88))
