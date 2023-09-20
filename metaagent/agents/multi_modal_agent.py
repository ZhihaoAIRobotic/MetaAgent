# from metaagent.actions import BossRequirement, WritePRD
from metaagent.agents.base_agent import Agent
from typing import Iterable
from metaagent.actions import action_dict


class MultiModelAgent(Agent):
    """
    Represents a Product Manager role responsible for product development and management.
    
    Attributes:
        name (str): Name of the product manager.
        profile (str): Role profile, default is 'Product Manager'.
        goal (str): Goal of the product manager.frp
        constraints (str): Constraints or limitations for the product manager.
    """
    
    def __init__(self, 
                 name: str = "Alice", 
                 profile: str = "MultiModelAgent", 
                 goal: str = "Efficiently create a successful product",
                 constraints: str = "",
                 **kwargs) -> None:
        """
        Initializes the ProductManager role with given attributes.
        
        Args:
            name (str): Name of the product manager.
            profile (str): Role profile.
            goal (str): Goal of the product manager.
            constraints (str): Constraints or limitations for the product manager.
        """
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions(['Say', 'DrawImage', 'MakeVideos'])
        self._watch(['UserInput'])

    def _init_actions(self, actions: Iterable[str]):
        """Put actions into all_states and all_actions, and set prefix for actions."""
        self._reset()
        for idx, action_name in enumerate(actions):
            print(action_name)
            i = action_dict[action_name]()
            print(i)
            i.set_prefix(self._get_prefix(), self.profile)
            self.all_actions.append(i)
            self.all_states.append(f"{idx}. {action_name}")
