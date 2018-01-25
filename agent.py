from copy import deepcopy


class Agent:
    """The parent class of all agents, uses principle of Agent Oriented Programming to share information between Agents

    The Agent Superclass sets the framework which allows agents to ask each other for data. An agent can be defined as a
    class that contains all necessary data and methods to perform a unique set of tasks individually, conceptually
    similar to how a human performs tasks.

    Agent Oriented Programming(AOP) seeks to model software development after how humans perform complex tasks in groups.
    When we need information from one another, we simply 'ask' each other for the data. Similarly, any agent class is
    able to ask another agent for any needed info. AOP does this through reflection, which allows agents to ask each other
    for specific variables at runtime (ex. this line: self.object_color = self.ask("eyes", "visible_object_color"),
    finds the variable named 'visible_object_color' within the 'eyes' agent class and returns that value).

    This passing of data by 'asking' allows data to be safely transferred between classes and prevents variables being
    changed when they shouldn't be. It also allows agents to call others functions and share data without requiring
    dependencies in code, which makes it easier to switch agent classes in and out as needed.

    It should be noted that AGENT CLASSES SHOULD ALWAYS BE STATIC. There should only be one instance of each
    agent subclass ever created. Similar to how there is only one of you (hopefully), each agent should have only one
    instance of itself in the program.
    """

    def __init__(self, agent_name, environment=None):
        """Assigns the agent it's name and environment based on passed parameters

        When an agent is created it is added the the private agent_list dictionary of this class. That dictionary allows
        agents to gather data from one another by using the ask and share methods rather than requiring a dependency
        in code.

        Key variables:
        environment:
        see the environment class. An environment defines what objects an agent has access to.
        __agent_list:
        a dictionary containing { agent_name: a string name of the agent => AgentObject: the actual instance of the agent}
        """
        self.agent_name = agent_name # the name of the agent, used in the __
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
