import asyncio
import uuid
from abc import abstractmethod, ABC
from typing import Any, Callable, Dict, Generic, List, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict

SignalValueT = TypeVar("SignalValueT")

# TODO: saqadri - handle signals properly that works with other execution backends like Temporal as well


class Signal(BaseModel, Generic[SignalValueT]):
    """Represents a signal that can be sent to a workflow."""

    name: str
    description: str | None = "Workflow Signal"
    payload: SignalValueT | None = None
    metadata: Dict[str, Any] | None = None
    workflow_id: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SignalRegistration(BaseModel):
    """Tracks registration of a signal handler."""

    signal_name: str
    unique_name: str
    workflow_id: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SignalHandler(Protocol, Generic[SignalValueT]):
    """Protocol for handling signals."""

    @abstractmethod
    async def signal(self, signal: Signal[SignalValueT]) -> None:
        """Emit a signal to all waiting handlers and registered callbacks."""

    @abstractmethod
    async def wait_for_signal(
        self,
        signal: Signal[SignalValueT],
        timeout_seconds: int | None = None,
    ) -> SignalValueT:
        """Wait for a signal to be emitted."""

    def on_signal(self, signal_name: str) -> Callable:
        """
        Decorator to register a handler for a signal.

        Example:
            @signal_handler.on_signal("approval_needed")
            async def handle_approval(value: str):
                print(f"Got approval signal with value: {value}")
        """


class PendingSignal(BaseModel):
    """Tracks a waiting signal handler and its event."""

    registration: SignalRegistration
    event: asyncio.Event | None = None
    value: SignalValueT | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseSignalHandler(ABC, Generic[SignalValueT]):
    """Base class implementing common signal handling functionality."""

    def __init__(self):
        # Map signal_name -> list of PendingSignal objects
        self._pending_signals: Dict[str, List[PendingSignal]] = {}
        # Map signal_name -> list of (unique_name, handler) tuples
        self._handlers: Dict[str, List[tuple[str, Callable]]] = {}
        self._lock = asyncio.Lock()

    async def cleanup(self, signal_name: str | None = None):
        """Clean up handlers and registrations for a signal or all signals."""
        async with self._lock:
            if signal_name:
                if signal_name in self._handlers:
                    del self._handlers[signal_name]
                if signal_name in self._pending_signals:
                    del self._pending_signals[signal_name]
            else:
                self._handlers.clear()
                self._pending_signals.clear()

    def validate_signal(self, signal: Signal[SignalValueT]):
        """Validate signal properties."""
        if not signal.name:
            raise ValueError("Signal name is required")
        # Subclasses can override to add more validation

    def on_signal(self, signal_name: str) -> Callable:
        """Register a handler for a signal."""

        def decorator(func: Callable) -> Callable:
            unique_name = f"{signal_name}_{uuid.uuid4()}"

            async def wrapped(value: SignalValueT):
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(value)
                    else:
                        func(value)
                except Exception as e:
                    # Log the error but don't fail the entire signal handling
                    print(f"Error in signal handler {signal_name}: {str(e)}")

            self._handlers.setdefault(signal_name, []).append((unique_name, wrapped))
            return wrapped

        return decorator

    @abstractmethod
    async def signal(self, signal: Signal[SignalValueT]) -> None:
        """Emit a signal to all waiting handlers and registered callbacks."""

    @abstractmethod
    async def wait_for_signal(
        self,
        signal: Signal[SignalValueT],
        timeout_seconds: int | None = None,
    ) -> SignalValueT:
        """Wait for a signal to be emitted."""


class ConsoleSignalHandler(SignalHandler[str]):
    """Simple console-based signal handling (blocks on input)."""

    def __init__(self):
        self._pending_signals: Dict[str, List[PendingSignal]] = {}
        self._handlers: Dict[str, List[Callable]] = {}

    async def wait_for_signal(self, signal, timeout_seconds=None):
        """Block and wait for console input."""
        print(f"\n[SIGNAL: {signal.name}] {signal.description}")
        if timeout_seconds:
            print(f"(Timeout in {timeout_seconds} seconds)")

        # Use asyncio.get_event_loop().run_in_executor to make input non-blocking
        loop = asyncio.get_event_loop()
        if timeout_seconds is not None:
            try:
                value = await asyncio.wait_for(
                    loop.run_in_executor(None, input, "Enter value: "), timeout_seconds
                )
            except asyncio.TimeoutError:
                print("\nTimeout waiting for input")
                raise
        else:
            value = await loop.run_in_executor(None, input, "Enter value: ")

        return value

        # value = input(f"[SIGNAL: {signal.name}] {signal.description}: ")
        # return value

    def on_signal(self, signal_name):
        def decorator(func):
            async def wrapped(value: SignalValueT):
                if asyncio.iscoroutinefunction(func):
                    await func(value)
                else:
                    func(value)

            self._handlers.setdefault(signal_name, []).append(wrapped)
            return wrapped

        return decorator

    async def signal(self, signal):
        print(f"[SIGNAL SENT: {signal.name}] Value: {signal.payload}")

        handlers = self._handlers.get(signal.name, [])
        await asyncio.gather(
            *(handler(signal) for handler in handlers), return_exceptions=True
        )

        # Notify any waiting coroutines
        if signal.name in self._pending_signals:
            for ps in self._pending_signals[signal.name]:
                ps.value = signal.payload
                ps.event.set()


class AsyncioSignalHandler(BaseSignalHandler[SignalValueT]):
    """
    Asyncio-based signal handling using an internal dictionary of asyncio Events.
    """

    async def wait_for_signal(
        self, signal, timeout_seconds: int | None = None
    ) -> SignalValueT:
        event = asyncio.Event()
        unique_name = str(uuid.uuid4())

        registration = SignalRegistration(
            signal_name=signal.name,
            unique_name=unique_name,
            workflow_id=signal.workflow_id,
        )

        pending_signal = PendingSignal(registration=registration, event=event)

        async with self._lock:
            # Add to pending signals
            self._pending_signals.setdefault(signal.name, []).append(pending_signal)

        try:
            # Wait for signal
            if timeout_seconds is not None:
                await asyncio.wait_for(event.wait(), timeout_seconds)
            else:
                await event.wait()

            return pending_signal.value
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Timeout waiting for signal {signal.name}") from e
        finally:
            async with self._lock:
                # Remove from pending signals
                if signal.name in self._pending_signals:
                    self._pending_signals[signal.name] = [
                        ps
                        for ps in self._pending_signals[signal.name]
                        if ps.registration.unique_name != unique_name
                    ]
                    if not self._pending_signals[signal.name]:
                        del self._pending_signals[signal.name]

    def on_signal(self, signal_name):
        def decorator(func):
            async def wrapped(value: SignalValueT):
                if asyncio.iscoroutinefunction(func):
                    await func(value)
                else:
                    func(value)

            self._handlers.setdefault(signal_name, []).append(wrapped)
            return wrapped

        return decorator

    async def signal(self, signal):
        async with self._lock:
            # Notify any waiting coroutines
            if signal.name in self._pending_signals:
                pending = self._pending_signals[signal.name]
                for ps in pending:
                    ps.value = signal.payload
                    ps.event.set()

        # Notify any registered handler functions
        tasks = []
        handlers = self._handlers.get(signal.name, [])
        for _, handler in handlers:
            tasks.append(handler(signal))

        await asyncio.gather(*tasks, return_exceptions=True)


# TODO: saqadri - check if we need to do anything to combine this and AsyncioSignalHandler
class LocalSignalStore:
    """
    Simple in-memory structure that allows coroutines to wait for a signal
    and triggers them when a signal is emitted.
    """

    def __init__(self):
        # For each signal_name, store a list of futures that are waiting for it
        self._waiters: Dict[str, List[asyncio.Future]] = {}

    async def emit(self, signal_name: str, payload: Any):
        # If we have waiting futures, set their result
        if signal_name in self._waiters:
            for future in self._waiters[signal_name]:
                if not future.done():
                    future.set_result(payload)
            self._waiters[signal_name].clear()

    async def wait_for(
        self, signal_name: str, timeout_seconds: int | None = None
    ) -> Any:
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self._waiters.setdefault(signal_name, []).append(future)

        if timeout_seconds is not None:
            try:
                return await asyncio.wait_for(future, timeout=timeout_seconds)
            except asyncio.TimeoutError:
                # remove the fut from list
                if not future.done():
                    self._waiters[signal_name].remove(future)
                raise
        else:
            return await future


class SignalWaitCallback(Protocol):
    """Protocol for callbacks that are triggered when a workflow pauses waiting for a given signal."""

    async def __call__(
        self,
        signal_name: str,
        request_id: str | None = None,
        workflow_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Receive a notification that a workflow is pausing on a signal.

        Args:
            signal_name: The name of the signal the workflow is pausing on.
            workflow_id: The ID of the workflow that is pausing (if using a workflow engine).
            metadata: Additional metadata about the signal.
        """
        ...
