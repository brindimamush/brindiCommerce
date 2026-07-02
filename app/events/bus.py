import asyncio
from typing import Callable, Dict, List, Any
import structlog

logger = structlog.get_logger()

class EventBus:
    def __init__(self):
        # Maps event names to a list of async callback functions
        self._subscribers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., Any]):
        """Register a callback function for a specific event."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
        logger.debug("Subscribed to event", event_name=event_name, callback=callback.__name__)

    async def publish(self, event_name: str, *args, **kwargs):
        """Trigger all callbacks associated with an event asynchronously."""
        if event_name not in self._subscribers:
            return

        callbacks = self._subscribers[event_name]
        logger.debug("Publishing event", event_name=event_name, listeners=len(callbacks))
        
        # Execute all listeners concurrently in the background
        tasks = [
            asyncio.create_task(self._execute_callback(callback, *args, **kwargs))
            for callback in callbacks
        ]
        
        # We don't await the tasks here so the main execution thread isn't blocked.
        # Fire-and-forget logic.

    async def _execute_callback(self, callback: Callable, *args, **kwargs):
        """Wrapper to safely execute a callback and catch any unhandled exceptions."""
        try:
            await callback(*args, **kwargs)
        except Exception as e:
            logger.error(
                "Event listener failed", 
                callback=callback.__name__, 
                error=str(e)
            )

event_bus = EventBus()