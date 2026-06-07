"""Server-Sent Events transport layer.

Public surface:

* :class:`SSEMessage`           — value object for one SSE frame.
* :class:`EventEncoder`         — abstract Protocol for event-to-frame encoding.
* :class:`SummaryEventEncoder`  — concrete encoder for summary events.
* :class:`SummaryEventStreamer` — orchestrates use case → SSE response.
"""

from app.api.sse.encoder import EventEncoder, SSEMessage, SummaryEventEncoder
from app.api.sse.streaming import SummaryEventStreamer

__all__ = [
    "EventEncoder",
    "SSEMessage",
    "SummaryEventEncoder",
    "SummaryEventStreamer",
]
