from metaagent.environment.environment import Environment


if __name__ == '__main__':
    workflow = '/home/lzh/CodeProject/DIMA/metaagent/workflow.yml'
    env = Environment(workflow)
    env.agents.add_agents('writer_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/writer_agent.yml')
    env.agents.add_agents('story_board_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/story_board_agent.yml', needs=['writer_agent'])
    env.agents.add_agents('cartoonist_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/cartoonist_agent.yml', needs=['story_board_agent'])
    env.run()
