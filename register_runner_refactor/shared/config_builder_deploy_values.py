class ConfigBuilderDeployValues:
    def __init__(self) -> None:
        self.default_runner_request_cpu = "100m"
        self.default_runner_request_memory = "200Mi"
        self.default_runner_command = [
            "/home/runner/run.sh"
        ]
        self.default_controller_service_account_name = "im-arc-cntlr-gha-rs-controller"
        self.default_controller_service_account_namespace = "arc-system"
        self.default_container_mode = "none"
        self.default_kubernetes_mode_volume_size = "1Gi"
        self.default_spec_containers_name = "listener"
        self.default_spec_containers_requests_cpu = "100m"
        self.default_spec_containers_requests_memory = "128Mi"

        self.options_container_mode = [
            "none",
            "dind",
            "kubernetes",
        ]

        self.runner_group = ""
        self.runner_request_cpu = ""
        self.runner_request_memory = ""
        self.runner_max_cpu = ""
        self.runner_max_memory = ""
        self.runner_agent_pool = ""
        self.runner_image = ""
        self.runner_tag = ""
        self.runner_sha = ""
        self.github_config_url = ""
        self.github_app_secret_name = ""
        self.max_runners = 0
        self.min_runners = 0
        self.listener_max_cpu = ""
        self.listener_max_memory = ""
        self.listener_agent_pool = ""
        self.runner_command = []
        self.labels = {}
        self.annotations = {}
        self.controller_service_account_name = ""
        self.controller_service_account_namespace = ""
        self.container_mode = ""
        self.kubernetes_mode_volume_size = ""

        self.spec_container_name = ""
        self.spec_container_image = ""

    def _combine_dicts(self, dict1: dict, dict2: dict) -> dict:
        combined = {**dict1, **dict2}
        return combined


    def create_values_json(self) -> dict:
        prometheus_annotations = {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080",
            "prometheus.io/path": "/metrics",
        }

        runner_prometheus_annotations = {}
        if self.runner_agent_pool != "linux":
            runner_prometheus_annotations = self._combine_dicts(prometheus_annotations, self.annotations)

        runner_annotations = self._combine_dicts(runner_prometheus_annotations, self.annotations)
        listener_annotations = self._combine_dicts(prometheus_annotations, self.annotations)

        helm_values = {
            "githubConfigUrl": self.github_config_url,
            "githubConfigSecret": self.github_app_secret_name,
            "maxRunners": self.max_runners,
            "minRunners": self.min_runners,
            "runnerGroup": self.runner_group,
            "controllerServiceAccount": {
                "name": self.controller_service_account_name,
                "namespace": self.controller_service_account_namespace,
            },
            "listenerTemplate": {
                "metadata": {
                    "annotations": listener_annotations,
                    "labels": self.labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": self.spec_container_name,
                            "image": self.spec_container_image,
                            "command": self.runner_command,
                            "resources": {
                                "limits": {
                                    "cpu": self.runner_max_cpu,
                                    "memory": self.runner_max_memory,
                                },
                                "requests": {
                                    "cpu": self.runner_request_cpu,
                                    "memory": self.runner_request_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": self.listener_agent_pool
                    }
                }
            },
            "template": {
                "metadata": {
                    "labels": self.labels,
                    "annotations": runner_annotations,
                },
                "spec": {
                    "containers": [
                        {
                            "name": self.spec_container_name,
                            "resources": {
                                "limits": {
                                    "cpu": self.listener_max_cpu,
                                    "memory": self.listener_max_memory,
                                },
                                "requests": {
                                    "cpu": self.runner_request_cpu,
                                    "memory": self.runner_request_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": self.runner_agent_pool
                    }
                }
            }
        }



        return helm_values
