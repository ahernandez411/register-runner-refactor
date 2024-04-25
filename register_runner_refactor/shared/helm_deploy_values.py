import copy
import os

from shared.static_values import StaticValues

class HelmDeployValues:
    def __init__(self) -> None:
        self._prometheus_annotations = {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080",
            "prometheus.io/path": "/metrics",
        }

        # hard-coded assignments
        self.github_app_secret_name = "dynamic-runners-gh-app"
        self.controller_service_account_name = "im-arc-cntlr-gha-rs-controller"
        self.controller_service_account_namespace = "arc-system"
        self.listener_spec_containers_name = "listener"
        self.listener_spec_containers_resources_limits_cpu = "300m"
        self.listener_spec_containers_resources_limits_memory = "500Mi"
        self.listener_spec_containers_resources_requests_cpu = "100m"
        self.listener_spec_containers_resources_requests_memory = "128Mi"
        self.listener_spec_node_selector_agentpool = "mgmt"
        self.runner_spec_containers_name = "runner"
        self.kubernetes_resources_requests_storage_size = "1Gi"

        self.github_config_url = f"https://github.com/{self._input_organization}"
        self.max_runners = None
        self.min_runners = None
        self.runner_group = self._input_runner_group

        self.listener_metadata_annotations = {}
        self.listener_metadata_labels = None
        self.runner_metadata_labels = None
        self.runner_metadata_annotations = {}
        self.runner_spec_containers_command = None
        self.runner_spec_containers_image = None
        self.runner_spec_containers_resources_limits_cpu = None
        self.runner_spec_containers_resources_limits_memory = None
        self.runner_spec_containers_resources_requests_cpu = None
        self.runner_spec_containers_resources_requests_memory = None
        self.runner_spec_node_selector_agentpool = None
        self.annotation_runner_image = None

        self._setup_metadata_labels()
        self._setup_min_max_runners()
        self._setup_runner_image_values()
        self._setup_container_resources()
        self._setup_runner_spec_container_image()

    @property
    def _input_runner_name(self):
        return os.getenv("RUNNER_NAME", None)

    @property
    def _input_runner_group(self):
        return os.getenv("RUNNER_GROUP", None)

    @property
    def _input_registry(self) -> str:
        return os.getenv("REGISTRY", None)

    @property
    def _input_platform(self) -> str:
        return os.getenv("PLATFORM", StaticValues.PLATFORM_LINUX)

    @property
    def _input_organization(self) -> str:
        return os.getenv("ORGANIZATION", None)

    @property
    def _input_image_tag(self) -> str:
        return os.getenv("IMAGE_TAG", None)

    @property
    def _input_image_sha(self):
        return os.getenv("IMAGE_SHA", None)

    @property
    def _input_image(self) -> str:
        input_image = os.getenv("IMAGE", None)
        return input_image

    @property
    def _input_environment(self) -> str:
        input_environment = os.getenv("TARGET_ENVIRONMENT", StaticValues.ENV_PROD).lower()
        return input_environment

    @property
    def _input_container_mode(self) -> str:
        input_container_mode = os.getenv("CONTAINER_MODE", StaticValues.CONTAINER_MODE_NONE).lower()
        return input_container_mode


    def _setup_metadata_labels(self) -> None:
        # Basic Assignment from environment variables
        labels = {
            "org": self._input_organization,
            "region": "na27" if "-secondary" in self._input_environment else "na26"
        }
        self.listener_metadata_labels = copy.copy(labels)
        self.runner_metadata_labels = copy.copy(labels)


    def _setup_min_max_runners(self):
        # More Complex Assignments
        if self._input_runner_name in StaticValues.RUNNERS_WITH_LARGE_LIMITS:
            self.max_runners = 30
            self.min_runners = 1
        else:
            self.max_runners = 10
            self.min_runners = 0


    def _setup_runner_image_values(self):
        if (
            not self._input_image or
            self._input_image.strip() == StaticValues.VALUE_NA or
            self._input_image.strip() == ""
        ):
            tag = self._input_image_sha if self._input_image_sha and self._input_image_sha.strip() != StaticValues.VALUE_NA else self._input_image_tag

            self.annotation_runner_image = f"{self._input_organization}/{self._input_runner_name}:{tag}"
            self.runner_image = f"{self._input_registry}/{self._input_organization}/{self._input_runner_name}"
        else:
            self.annotation_runner_image = f"{self._input_runner_name}:{self._input_image_tag}"
            self.runner_image = f"{self._input_registry}/{self._input_image}"


    def _setup_container_resources(self):
        self.listener_metadata_annotations = copy.copy(self._prometheus_annotations)
        self.listener_metadata_annotations["runnerImage"] = self.annotation_runner_image

        if self._input_platform == StaticValues.PLATFORM_LINUX:
            self.runner_metadata_annotations["runnerImage"] = self.annotation_runner_image
            self.runner_spec_containers_command = [
                "/home/runner/run.sh"
            ]
            self.runner_spec_containers_resources_limits_cpu = "1500m"
            self.runner_spec_containers_resources_limits_memory = "3Gi"
            self.runner_spec_containers_resources_requests_cpu = "100m"
            self.runner_spec_containers_resources_requests_memory = "200Mi"
            self.runner_spec_node_selector_agentpool = StaticValues.PLATFORM_LINUX

        else:
            self.runner_metadata_annotations = copy.copy(self._prometheus_annotations)
            self.runner_metadata_annotations["runnerImage"] = self.annotation_runner_image
            self.runner_spec_containers_command = [
                "cmd.exe",
                "/c",
                "\\home\\runner\\run.cmd"
            ]
            self.runner_spec_containers_resources_limits_cpu = "3000m"
            self.runner_spec_containers_resources_limits_memory = "6Gi"
            self.runner_spec_containers_resources_requests_cpu = "500m"
            self.runner_spec_containers_resources_requests_memory = "2Gi"
            self.runner_spec_node_selector_agentpool = StaticValues.PLATFORM_WINDOWS


    def _setup_runner_spec_container_image(self):
        if "sha256" in self._input_image_sha.lower():
            self.runner_spec_containers_image = f"{self.runner_image}@{self._input_image_sha}"
        else:
            self.runner_spec_containers_image = f"{self.runner_image}:{self._input_image_tag}"


    def create_helm_json(self) -> dict:
        helm_json = {
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
                    "annotations": self.listener_metadata_annotations,
                    "labels": self.listener_metadata_labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": self.listener_spec_containers_name,
                            "resources": {
                                "limits": {
                                    "cpu": self.listener_spec_containers_resources_limits_cpu,
                                    "memory": self.listener_spec_containers_resources_limits_memory,
                                },
                                "requests": {
                                    "cpu": self.listener_spec_containers_resources_requests_cpu,
                                    "memory": self.listener_spec_containers_resources_requests_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": self.listener_spec_node_selector_agentpool
                    }
                }
            },
            "template": {
                "metadata": {
                    "labels": self.runner_metadata_labels,
                    "annotations": self.runner_metadata_annotations,
                },
                "spec": {
                    "containers": [
                        {
                            "command": self.runner_spec_containers_command,
                            "name": self.runner_spec_containers_name,
                            "image": self.runner_spec_containers_image,
                            "resources": {
                                "limits": {
                                    "cpu": self.runner_spec_containers_resources_limits_cpu,
                                    "memory": self.runner_spec_containers_resources_limits_memory,
                                },
                                "requests": {
                                    "cpu": self.runner_spec_containers_resources_requests_cpu,
                                    "memory": self.runner_spec_containers_resources_requests_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": self.runner_spec_node_selector_agentpool
                    }
                }
            }
        }

        if self._input_container_mode == StaticValues.CONTAINER_MODE_DIND:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_DIND,
            }

        elif self._input_container_mode == StaticValues.CONTAINER_MODE_KUBERNETES:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_KUBERNETES,
                "kubernetesModeWorkVolumeClaim" : {
                    "accessModes": [ "ReadWriteOnce" ],
                    "storageClassName": "dynamic-blob-storage",
                    "resources": {
                        "requests": {
                            "storage": self.kubernetes_resources_requests_storage_size
                        }
                    }
                },
                "kubernetesModeServiceAccount": {
                    "annotations": {
                        "name": "gha-runner-kb-mode-sa"
                    }
                }
            }
            helm_json["template"]["spec"]["containers"][0]["env"] = [
                {
                    "name": "ACTIONS_RUNNER_REQUIRE_JOB_CONTAINER",
                    "value": "false"
                }
            ]

        return helm_json




