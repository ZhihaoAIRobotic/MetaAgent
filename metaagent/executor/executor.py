import asyncio
import functools
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    TYPE_CHECKING,
)

from pydantic import BaseModel, ConfigDict

from metaagent.context_dependent import ContextDependent
from metaagent.executor.workflow_signal import (
    AsyncioSignalHandler,
    Signal,
    SignalHandler,
    SignalValueT,
)
from metaagent.logging.logger import get_logger

if TYPE_CHECKING:
    from metaagent.context import Context

logger = get_logger(__name__)

# Type variable for the return type of tasks
R = TypeVar("R")


class ExecutorConfig(BaseModel):
    """Configuration for executors."""

    max_concurrent_activities: int | None = None  # Unbounded by default
    timeout_seconds: timedelta | None = None  # No timeout by default
    retry_policy: Dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class Executor(ABC, ContextDependent):
    """Abstract base class for different execution backends"""

    def __init__(
        self,
        engine: str,
        config: ExecutorConfig | None = None,
        signal_bus: SignalHandler = None,
        context: Optional["Context"] = None,
        **kwargs,
    ):
        super().__init__(context=context, **kwargs)
        self.execution_engine = engine

        if config:
            self.config = config
        else:
            # TODO: saqadri - executor config should be loaded from settings
            # ctx = get_current_context()
            self.config = ExecutorConfig()

        self.signal_bus = signal_bus

    @asynccontextmanager
    async def execution_context(self):
        """Context manager for execution setup/teardown."""
        try:
            yield
        except Exception as e:
            # TODO: saqadri - add logging or other error handling here
            raise e

    @abstractmethod
    async def execute(
        self,
        *tasks: Callable[..., R] | Coroutine[Any, Any, R],
        **kwargs: Any,
    ) -> List[R | BaseException]:
        """Execute a list of tasks and return their results"""

    @abstractmethod
    async def execute_streaming(
        self,
        *tasks: List[Callable[..., R] | Coroutine[Any, Any, R]],
        **kwargs: Any,
    ) -> AsyncIterator[R | BaseException]:
        """Execute tasks and yield results as they complete"""

    async def map(
        self,
        func: Callable[..., R],
        inputs: List[Any],
        **kwargs: Any,
    ) -> List[R | BaseException]:
        """
        Run `func(item)` for each item in `inputs` with concurrency limit.
        """
        results: List[R, BaseException] = []

        async def run(item):
            if self.config.max_concurrent_activities:
                semaphore = asyncio.Semaphore(self.config.max_concurrent_activities)
                async with semaphore:
                    return await self.execute(functools.partial(func, item), **kwargs)
            else:
                return await self.execute(functools.partial(func, item), **kwargs)

        coros = [run(x) for x in inputs]
        # gather all, each returns a single-element list
        list_of_lists = await asyncio.gather(*coros, return_exceptions=True)

        # Flatten results
        for entry in list_of_lists:
            if isinstance(entry, list):
                results.extend(entry)
            else:
                # Means we got an exception at the gather level
                results.append(entry)

        return results

    async def validate_task(
        self, task: Callable[..., R] | Coroutine[Any, Any, R]
    ) -> None:
        """Validate a task before execution."""
        if not (asyncio.iscoroutine(task) or asyncio.iscoroutinefunction(task)):
            raise TypeError(f"Task must be async: {task}")

    async def signal(
        self,
        signal_name: str,
        payload: SignalValueT = None,
        signal_description: str | None = None,
    ) -> None:
        """
        Emit a signal.
        """
        signal = Signal[SignalValueT](
            name=signal_name, payload=payload, description=signal_description
        )
        await self.signal_bus.signal(signal)

    async def wait_for_signal(
        self,
        signal_name: str,
        request_id: str | None = None,
        workflow_id: str | None = None,
        signal_description: str | None = None,
        timeout_seconds: int | None = None,
        signal_type: Type[SignalValueT] = str,
    ) -> SignalValueT:
        """
        Wait until a signal with signal_name is emitted (or timeout).
        Return the signal's payload when triggered, or raise on timeout.
        """

        # Notify any callbacks that the workflow is about to be paused waiting for a signal
        if self.context.signal_notification:
            self.context.signal_notification(
                signal_name=signal_name,
                request_id=request_id,
                workflow_id=workflow_id,
                metadata={
                    "description": signal_description,
                    "timeout_seconds": timeout_seconds,
                    "signal_type": signal_type,
                },
            )

        signal = Signal[signal_type](
            name=signal_name, description=signal_description, workflow_id=workflow_id
        )
        return await self.signal_bus.wait_for_signal(signal)


class AsyncioExecutor(Executor):
    """Default executor using asyncio"""

    def __init__(
        self,
        config: ExecutorConfig | None = None,
        signal_bus: SignalHandler | None = None,
    ):
        signal_bus = signal_bus or AsyncioSignalHandler()
        super().__init__(engine="asyncio", config=config, signal_bus=signal_bus)

        self._activity_semaphore: asyncio.Semaphore | None = None
        if self.config.max_concurrent_activities is not None:
            self._activity_semaphore = asyncio.Semaphore(
                self.config.max_concurrent_activities
            )

    async def _execute_task(
        self, task: Callable[..., R] | Coroutine[Any, Any, R], **kwargs: Any
    ) -> R | BaseException:
        async def run_task(task: Callable[..., R] | Coroutine[Any, Any, R]) -> R:
            try:
                if asyncio.iscoroutine(task):
                    return await task
                elif asyncio.iscoroutinefunction(task):
                    return await task(**kwargs)
                else:
                    # Execute the callable and await if it returns a coroutine
                    loop = asyncio.get_running_loop()

                    # If kwargs are provided, wrap the function with partial
                    if kwargs:
                        wrapped_task = functools.partial(task, **kwargs)
                        result = await loop.run_in_executor(None, wrapped_task)
                    else:
                        result = await loop.run_in_executor(None, task)

                    # Handle case where the sync function returns a coroutine
                    if asyncio.iscoroutine(result):
                        return await result

                    return result
            except Exception as e:
                # TODO: saqadri - adding logging or other error handling here
                return e

        if self._activity_semaphore:
            async with self._activity_semaphore:
                return await run_task(task)
        else:
            return await run_task(task)

    async def execute(
        self,
        *tasks: Callable[..., R] | Coroutine[Any, Any, R],
        **kwargs: Any,
    ) -> List[R | BaseException]:
        # TODO: saqadri - validate if async with self.execution_context() is needed here
        async with self.execution_context():
            return await asyncio.gather(
                *(self._execute_task(task, **kwargs) for task in tasks),
                return_exceptions=True,
            )

    async def execute_streaming(
        self,
        *tasks: List[Callable[..., R] | Coroutine[Any, Any, R]],
        **kwargs: Any,
    ) -> AsyncIterator[R | BaseException]:
        # TODO: saqadri - validate if async with self.execution_context() is needed here
        async with self.execution_context():
            # Create futures for all tasks
            futures = [
                asyncio.create_task(self._execute_task(task, **kwargs))
                for task in tasks
            ]
            pending = set(futures)

            while pending:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )
                for future in done:
                    yield await future

    async def signal(
        self,
        signal_name: str,
        payload: SignalValueT = None,
        signal_description: str | None = None,
    ) -> None:
        await super().signal(signal_name, payload, signal_description)

    async def wait_for_signal(
        self,
        signal_name: str,
        request_id: str | None = None,
        workflow_id: str | None = None,
        signal_description: str | None = None,
        timeout_seconds: int | None = None,
        signal_type: Type[SignalValueT] = str,
    ) -> SignalValueT:
        return await super().wait_for_signal(
            signal_name,
            request_id,
            workflow_id,
            signal_description,
            timeout_seconds,
            signal_type,
        )
