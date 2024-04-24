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

        self.option_container_mode_none = "none"
        self.option_container_mode_dind = "dind"
        self.option_container_mode_kubernetes = "kubernetes"

        self.runner_group = ""
        self.runner_request_cpu = "100m"
        self.runner_request_memory = "200Mi"
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

        self.listener_container_name = "listener"
        self.runner_container_name = "runner"

        self.listener_requests_cpu = "100m"
        self.listener_requests_memory = "128Mi"

        self.runner_container_image = ""


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

        if "sha256" in self.runner_sha.lower():
            self.runner_container_image = f"{self.runner_image}@{self.runner_sha}"
        else:
            self.runner_container_image = f"{self.runner_image}:{self.runner_tag}"

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
                            "name": self.listener_container_name,
                            "resources": {
                                "limits": {
                                    "cpu": self.listener_max_cpu,
                                    "memory": self.listener_max_memory,
                                },
                                "requests": {
                                    "cpu": self.listener_requests_cpu,
                                    "memory": self.listener_requests_memory,
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
                            "command": self.runner_command,
                            "name": self.runner_container_name,
                            "image": self.runner_container_image,
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
                        "agentpool": self.runner_agent_pool
                    }
                }
            }
        }

        if self.container_mode == self.option_container_mode_dind:
            helm_values["containerMode"] = {
                "type": self.option_container_mode_dind,
            }

        elif self.container_mode == self.option_container_mode_kubernetes:
            helm_values["containerMode"] = {
                "type": self.option_container_mode_kubernetes,
                "kubernetesModeWorkVolumeClaim" : {
                    "accessModes": [ "ReadWriteOnce" ],
                    "storageClassName": "dynamic-blob-storage",
                    "resources": {
                        "requests": {
                            "storage": self.kubernetes_mode_volume_size
                        }
                    }
                },
                "kubernetesModeServiceAccount": {
                    "annotations": {
                        "name": "gha-runner-kb-mode-sa"
                    }
                }
            }
            helm_values["template"]["spec"]["containers"][0]["env"] = [
                {
                    "name": "ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER",
                    "value": "false"
                }
            ]

        return helm_values
