
class AgentCapabilities:
    pass

class AgentSkill:
    def __init__(self, id, name, description, tags, examples):
        pass

class AgentCard:
    def __init__(self, name, description, url, defaultInputModes, defaultOutputModes, skills, version, capabilities):
        pass

class AgentMessage:
    def __init__(self, type, text=None, content=None):
        self.type = type
        self.text = text
        self.content = content
