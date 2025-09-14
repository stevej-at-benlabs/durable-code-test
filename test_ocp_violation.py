"""
Example file with Open-Closed Principle violations for testing
"""


class OrderProcessor:
    """Violates OCP - needs modification for each new order type"""

    def process_order(self, order):
        # Bad: Switch statement that requires modification for new types
        if order.type == "standard":
            return self._process_standard(order)
        elif order.type == "express":
            return self._process_express(order)
        elif order.type == "priority":
            return self._process_priority(order)
        # Adding a new order type requires modifying this method

    def _process_standard(self, order):
        print(f"Processing standard order: {order.id}")
        return {"status": "processed", "shipping": "5-7 days"}

    def _process_express(self, order):
        print(f"Processing express order: {order.id}")
        return {"status": "processed", "shipping": "2-3 days"}

    def _process_priority(self, order):
        print(f"Processing priority order: {order.id}")
        return {"status": "processed", "shipping": "1 day"}


class PaymentGateway:
    """Another OCP violation - hardcoded payment methods"""

    def process_payment(self, amount, method):
        # Bad: Hardcoded payment methods, needs modification for new ones
        if method == "credit_card":
            return self._charge_credit_card(amount)
        elif method == "paypal":
            return self._charge_paypal(amount)
        elif method == "bitcoin":
            return self._charge_bitcoin(amount)
        else:
            raise ValueError(f"Unknown payment method: {method}")

    def _charge_credit_card(self, amount):
        print(f"Charging ${amount} to credit card")
        return True

    def _charge_paypal(self, amount):
        print(f"Charging ${amount} via PayPal")
        return True

    def _charge_bitcoin(self, amount):
        print(f"Charging {amount} BTC")
        return True