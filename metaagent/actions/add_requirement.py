#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/20 17:46
@Author  : alexanderwu
@File    : add_requirement.py
"""
from metaagent.actions.action import Action


class BossRequirement(Action):
    """Boss Requirement without any implementation details"""
    def run(self, *args, **kwargs):
        raise NotImplementedError
