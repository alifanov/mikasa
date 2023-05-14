from datetime import datetime
from unittest import TestCase

import pytest

from mikasa import LimitOrder, OrderType, TrailingStopLossOrder
from mikasa.orders import StopOrder


class OrderTestCase(TestCase):
    def test_limit_order_buy(self):
        dt = datetime.utcnow()
        order = LimitOrder(type=OrderType.BUY, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(high=120, low=110, fund=0, balance=100))
        self.assertTrue(order.can_be_executed(high=90, low=88, fund=0, balance=100))
        self.assertFalse(order.can_be_executed(high=90, low=88, fund=0, balance=50))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, 1)
        self.assertEqual(dbalance, -99.9)

    def test_limit_order_sell(self):
        dt = datetime.utcnow()
        order = LimitOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None)
        self.assertTrue(order.can_be_executed(high=120, low=110, fund=1, balance=100))
        self.assertFalse(order.can_be_executed(high=120, low=110, fund=0, balance=100))
        self.assertFalse(order.can_be_executed(high=90, low=88, fund=1, balance=100))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, -1)
        self.assertEqual(dbalance, 99.9)

    def test_stop_order_buy(self):
        dt = datetime.utcnow()
        order = StopOrder(type=OrderType.BUY, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(high=90, low=88, fund=0, balance=100))
        self.assertTrue(order.can_be_executed(high=120, low=110, fund=0, balance=100))
        self.assertFalse(order.can_be_executed(high=120, low=110, fund=0, balance=90))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, 1)
        self.assertEqual(dbalance, -99.9)

    def test_stop_order_sell(self):
        dt = datetime.utcnow()
        order = StopOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(high=120, low=110, fund=1, balance=0))
        self.assertTrue(order.can_be_executed(high=90, low=88, fund=1, balance=0))
        dfund, dbalance = order.execute(dt, commission_fraction=0.001)
        self.assertEqual(dfund, -1)
        self.assertEqual(dbalance, 99.9)

    def test_trailing_stop_loss_order_sell(self):
        order = TrailingStopLossOrder(type=OrderType.SELL, price=100, volume=1, executed_at=None, trail_percent=0.2)
        self.assertFalse(order.can_be_executed(high=110, low=109, fund=1, balance=0))
        self.assertTrue(order.can_be_executed(high=102, low=99, fund=1, balance=0))
        self.assertEqual(order.price, 100)
        order.update_trailing_state(high=200, low=150)
        self.assertEqual(order.price, 120)

    def test_bad_order_type_for_limit_order(self):
        order = LimitOrder(type=3, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(1, 2, 1, 1))

    def test_bad_order_type_execute(self):
        order = LimitOrder(type=3, price=100, volume=1, executed_at=None)
        with pytest.raises(ValueError):
            order.execute(None, 0)

    def test_bad_order_type_2(self):
        order = StopOrder(type=3, price=100, volume=1, executed_at=None)
        self.assertFalse(order.can_be_executed(1, 2, 1, 1))
