        action_selection_prompt = self.profile + observation
        print(action_selection_prompt)
        LOGGER.debug(action_selection_prompt)
        self.action, token_cost = self._llm.aask(action_selection_prompt)
        LOGGER.debug("****************Action****************/n")
        LOGGER.debug(self.action)

        try:
            start = self.action.find('{')
            end = self.action.rfind('}') + 1
            self.action = self.action[start:end]
            print(self.action)
            self.action = json.loads(self.action)
        except Exception:
            raise ValueError("The generated action is not in the correct format.")
        self.action = self.action['action']

        LOGGER.debug(self.action)
        self.action: Action = get_agent_action(self.action)()
        if self.action.params is None:
            self.action_params = None
            return 0
        action_params_prompt = ACTION_TEMPLATE.format(action=self.action.name, action_params=self.action.params, action_rules=self.action.rules, action_example=self.action.example)
        action_params_prompt = action_params_prompt + observation
        LOGGER.debug(action_params_prompt)
        self.action_params, token_cost = self._llm.aask(action_params_prompt)
        LOGGER.debug("****************ActionParam****************/n")
        LOGGER.debug(self.action_params)