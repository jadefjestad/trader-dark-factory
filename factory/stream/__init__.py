"""Pure building blocks for the streaming paper tier (issue #69, docs/streaming-design.md).

Nothing here opens a socket or places an order: the container wires these to Alpaca's websocket and
the paper broker. Every piece takes explicit timestamps so it is deterministic and testable.
"""
