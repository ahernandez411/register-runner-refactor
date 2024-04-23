from typing import List

class Values:
    def __init__(self) -> None:
        self.github_config_url = ""
        self.github_config_secret = "dynamic-runners-gh-app"
        self.max_runners = 10
        self.min_runners = 0
        self.runner_group = "dynamic-runners"


class ControllerServiceAccount:
    def __init__(self) -> None:
        self.name = ""
        self.namespace = ""



class ListenerTemplate:
    def __init__(self):
        self.metadata = Metadata()
        self.spec = Spec()


class Template:
    def __init__(self) -> None:
        self.metadata = Metadata()
        self.spec = Spec()



class Metadata:
    def __init__(self) -> None:
        self.annotations = Annotations()
        self.labels = Labels()


class Annotations:
    def __init__(self) -> None:
        self.runner_image = ""
        self.prometheus_io_scrape = "true"
        self.prometheus_io_port = "8080"
        self.prometheus_io_path = "/metrics"


class Labels:
    def __init__(self) -> None:
        self.org = ""
        self.region = ""


class Spec:
    def __init__(self) -> None:
        self.containers: List[Containers] = []
        self.node_selector = NodeSelector()



class Containers:
    def __init__(self) -> None:
        self.name = ""
        self.image = ""
        self.command = []
        self.resources = Resources()


class Resources:
    def __init__(self) -> None:
        self.limits = Limits()
        self.requests = Requests()


class Limits:
    def __init__(self) -> None:
        self.cpu = ""
        self.memory = ""


class Requests:
    def __init__(self) -> None:
        self.cpu = ""
        self.memory = ""



class NodeSelector:
    def __init__(self) -> None:
        self.agent_pool = ""
