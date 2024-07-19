# -*- coding: UTF-8 -*-
import importlib
import os
import sys
from absl import logging


class Register:
    """Module register"""

    def __init__(self, registry_name):
        self._dict = {}
        self._name = registry_name

    def __setitem__(self, key, value):
        if not callable(value):
            raise Exception("Value of a Registry must be a callable.")
        if key is None:
            key = value.__name__
        if key in self._dict:
            logging.warning("Key %s already in registry %s." % (key, self._name))
        self._dict[key] = value

    def register(self, target):
        """Decorator to register a function or class."""

        def decorator(key, value):
            if not callable(value):
                raise Exception(f"Error:{value} must be callable!")
            if key in self._dict:
                print(f"\033[31mWarning:\033[0m {value.__name__} already exists and will be overwritten!")
            self[key] = value
            return value

        if callable(target):
            # @reg.register
            return decorator(None, target)
        # @reg.register('alias')
        return lambda x: decorator(target, x)

    def __getitem__(self, key):
        try:
            return self._dict[key]
        except Exception as e:
            logging.error(f"module {key} not found: {e}")
            raise e

    def __contains__(self, key):
        return key in self._dict

    def keys(self):
        """key"""
        return self._dict.keys()


_AGENT_ACTIONS = {}


def register_agent_action(cls):
    """
    Registers an agent action class.

    This decorator should be used to decorate agent action classes.
    The decorated class will be added to a registry of agent actions,
    which can be accessed using the `get_agent_action` function.

    Example:
        >>> @register_agent_action
        ... class MyAction:
        ...     def __call__(self, *args, **kwargs):
        ...         # Action logic here
        ...         pass
        >>> get_agent_action("MyAction")
        <class '__main__.MyAction'>

    Args:
        cls (type): The agent action class to register.

    Returns:
        type: The registered agent action class.
    """
    global _AGENT_ACTIONS
    print(cls.__name__)
    _AGENT_ACTIONS[cls.__name__] = cls
    return cls


def get_agent_action(name: str):
    """
    Returns the registered agent action class with the given name.

    Args:
        name (str): The name of the agent action class to retrieve.

    Returns:
        type: The registered agent action class, or None if no agent action
              class with the given name is found.

    Raises:
        ValueError: If no agent action class with the given name is found.
    """
    global _AGENT_ACTIONS
    print(_AGENT_ACTIONS)
    if name in _AGENT_ACTIONS:
        return _AGENT_ACTIONS[name]
    else:
        raise ValueError(f"No agent action named {name} found.")