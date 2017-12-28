from copy import deepcopy


class Agent:
    """The parent class of all agents

    The Agent Superclass sets the framework by which all agents can perform their tasks. An agent can be defined as a
    class that contains all necessary data and methods to perform a unique set of tasks individually. Agent Oriented
    Programming(AOP) is centered around all functions of a program being performed by agents which work together through
    a hierarchy of managers and employees.

    AOP seeks to model software development after how humans perform complex tasks in groups. Each individual in a group
    has the understanding and skills to achieve their tasks independent of other coworkers. Just as we cannot directly
    change the data within someone's mind, AOP develops data integrity by preventing agents changing the member
    variables of one another unless they specifically ask for such information. If information is required by an
    individual they can ask the other agent for said data and then update they information. This convention improves
    modularity, scalability, and cohesion for each agent.
    """

    def __init__(self, agent_name, environment=None):
        """Assigns the agent it's name and environment based on passed parameters

        When an agent is created it is added the the private agent_list member variable of this class. That list allows
        agents to gather data from one another by using the ask and share methods rather than requiring a dependency
        in code.

        Key variables:
        environment: see the environment class. An environment defines what objects an agent has access to.
        """
        self.agent_name = agent_name
        if Agent.environment is None:
            Agent.environment = environment
        Agent.__agent_list[agent_name] = self

    __agent_list = {}
    environment = None

    def ask(self, agent_name, variable_name):
        """creates a deep copy of a member variable from one agent to another"""
        agent = Agent.__agent_list[agent_name]
        return deepcopy(getattr(agent, variable_name))

    def share(self, agent_name, variable_name):
        """shares an object between agents. This allows both of them to change attributes of said object"""
        agent = Agent.__agent_list[agent_name]
        return getattr(agent, variable_name)

    def report(self, manager, data_name, data):
        """sends updated information to a manger or coworker agent"""
        manager.collected_info[self.agent_name + "." + data_name] = data
