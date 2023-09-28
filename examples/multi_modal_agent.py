from metaagent.environment.environment import Environment


if __name__ == '__main__':
    workflow = '/home/lzh/CodeProject/DIMA/metaagent/workflow.yml'
    env = Environment(workflow)
    env.agents.add_agents('multimodal_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/multi_modal_agent.yml')
    env.run()
