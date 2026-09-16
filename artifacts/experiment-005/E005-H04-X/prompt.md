An order placement spans stock, payment, an order record, and an outbox
notification. If the final notification step fails, the earlier work should
be undone so the failed attempt does not consume capacity or leave an active
authorization. Repair the failure path while preserving the normal successful
stage order and the behavior when payment is declined.

Run the available test suite with:

    PYTHONPATH=src python -m unittest discover -s tests -v
