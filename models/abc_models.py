from abc import ABC, abstractmethod
from datetime import datetime

class IdentifiableEntity(ABC):
    def __init__(self, entity_id):
        self._entity_id = entity_id

    @abstractmethod
    def get_summary(self):
        pass

class BaseContent(ABC):
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    @abstractmethod
    def get_info(self):
        pass
