ACTION_AGENT_TEMPLATE = '''
You are an AI Agent. You have the following goals:
{agent_goal}

Please follow the goals to complete the task. You can choose to do the following actions:
{agent_actions}

There is some examples:
{agent_example}

Now, for a new observation, please select the action.
Here is the observation:

'''

ACTION_TEMPLATE = '''
You must Generate a json string. The json string should include the action you choose to do and the parameters.
The parameters of the {action} includes:
{action_params}
You need to follow the following rules to generate the parameters:
{action_rules}
Here is an example:
{action_example}
Now, for a new observation, please generate the json string, remember that the output must be a json string including the action name and the parameters.:

'''

single_round_observation = '''
human instruction: {instruction}
Retrived text: {retrived_text}
'''

OBSERVATION_TEMPLATE_DICT = {
    "single_round_observation": single_round_observation,
}


EXAMPLE_TEMPLATE = '''
Here is an example:
{example}
'''

CONVERSATIONAL_AGENT_TEMPLATE = '''
You are an AI Agent. You have the following goals:
{agent_goal}
{agent_example}
Now, please follow the goals to chat with the user.
Here is the history of the conversation:
'''