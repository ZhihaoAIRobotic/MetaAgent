# reference: llm-reasoners
from typing import Generic, TypeVar, Union, NamedTuple, Protocol, Optional, runtime_checkable, Tuple
from abc import ABC, abstractmethod


State = TypeVar("State")
Action = TypeVar("Action")
Example = TypeVar("Example")
Trace = tuple[list[State], list[Action]]
    

class Dynamics(ABC, Generic[State, Action]):

    @abstractmethod
    def init_state(self) -> State: ...

    @abstractmethod
    def step(self, state: State, action: Action) -> Union[State, Tuple[State, dict]]:
        """ Returns the next state and optionally an auxiliary data dict

        :param state: The current state
        :param action: The action to take
        :return: The next state and optionally an auxiliary data dict
        """
        ...

    @abstractmethod
    def is_terminal(self, state: State) -> bool: ...

class WorldModel(Dynamics, Generic[State, Action, Example]):
    def __init__(self) -> None:
        self.example = None
        self.prompt = None

    def update_example(self, example: Example, prompt = None) -> None:        
        if prompt is not None:
            self.prompt = prompt
        self.example = example

class DefaultWorldModel(WorldModel):
    # A default implementation of WorldModel that only 
    # saves the action sequence as the state

    def __init__(self, base_model) -> None:
        super().__init__()
        self.base_model = base_model

    def init_state(self):
        return []

    def step(self, state, action):
        return state + [action], {}

    def is_terminal(self, state):
        # By default the state is never terminal
        return False
    

class SearchConfig(ABC, Generic[State, Action, Example]):
    def __init__(self) -> None:
        self.example = None
        self.prompt = None

    @abstractmethod
    def get_actions(self, state: State) -> list[Action]: ...

    def fast_reward(self, state: State, action: Action) -> tuple[float, dict]:
        return 0, {}

    @abstractmethod
    def reward(self, state, action, **kwargs) -> tuple[float, dict]: ...

    def update_example(self, example: Example, prompt = None) -> None:
        if prompt is not None:
            self.prompt = prompt
        self.example = example


@runtime_checkable
class AlgorithmOutput(Protocol[State]):
    terminal_state: State
    trace: Trace

class SearchAlgorithm(ABC):
    def __init__(self, **kwargs): ...

    @abstractmethod
    def __call__(self, world_model: WorldModel, search_config: SearchConfig, **kwargs) -> AlgorithmOutput: ...


class Reasoner(ABC, Generic[State, Action, Example]):
    def __init__(self,
                 world_model: Dynamics[State, Action],
                 search_config: SearchConfig[State, Action, Example],
                 search_algo: SearchAlgorithm) -> None:
        self.dynamics = world_model
        self.search_config = search_config
        self.search_algo = search_algo

    def __call__(self, example: Optional[Example] = None, prompt = None, **kwargs) -> AlgorithmOutput[State]:
        if isinstance(self.dynamics, WorldModel):
            if example is None:
                raise ValueError("An example must be provided when using WorldModel")
            self.dynamics.update_example(example, prompt=prompt)
            self.search_config.update_example(example, prompt=prompt)
        return self.search_algo(self.dynamics, self.search_config, **kwargs)