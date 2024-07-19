REFLECT_TEMPLATE = '''
You need to reflect on the current task.
Your task is to {task}.
Your action feedback is {feedback}.
You need to reflect on the feedback and improve your action.
You can choose to {action}.
Your need to output a json string to the agent. The json string should include the action you choose to do and the parameters.
Here is an example:
{example}
'''
