import copy

from shared.workflow_inputs import WorkflowInputs
from typing import Tuple

class HelmDeployValues:
    def __init__(self) -> None:
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
        self.container_kubernetes_resources_requests_storage_size = "1Gi"

        # Asssignments from environment variables
        inputs = WorkflowInputs()

        self.container_mode = inputs.container_mode
        self.github_config_url = f"https://github.com/{inputs.organization}"
        self.runner_group = inputs.runner_group

        self.listener_metadata_labels = self._setup_listener_metadata_labels(inputs)
        self.runner_metadata_labels = self._setup_runner_metadata_labels(inputs)
        self.min_runners, self.max_runners = self._setup_min_max_runners(inputs)

        self.annotation_runner_image = self._setup_annotation_runner_image_values(inputs)
        self.runner_image = self._setup_runner_image_values(inputs)

        # Assignments from environmental variables and other values
        prometheus_annotations = {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080",
            "prometheus.io/path": "/metrics",
        }
        self.listener_metadata_annotations = self._setup_listener_metadata_annotations(inputs, prometheus_annotations, self.annotation_runner_image)

        self.runner_metadata_annotations = {}
        self.runner_spec_containers_command = None
        self.runner_spec_containers_resources_limits_cpu = None
        self.runner_spec_containers_resources_limits_memory = None
        self.runner_spec_containers_resources_requests_cpu = None
        self.runner_spec_containers_resources_requests_memory = None
        self.runner_spec_node_selector_agentpool = None
        self._setup_container_resources(inputs, prometheus_annotations, self.annotation_runner_image)

        self.runner_spec_containers_image = self._setup_runner_spec_container_image(inputs, self.runner_image)


    def _setup_runner_metadata_labels(self, inputs: WorkflowInputs) -> dict:
        # Basic Assignment from environment variables
        runner_metadata_labels = {
            "org": inputs.organization,
            "region": self._get_region(inputs)
        }
        return runner_metadata_labels


    def _setup_listener_metadata_labels(self, inputs: WorkflowInputs) -> dict:
        # Basic Assignment from environment variables
        listener_metadata_labels = {
            "org": inputs.organization,
            "region": self._get_region(inputs)
        }
        return listener_metadata_labels


    def _get_region(self, inputs: WorkflowInputs) -> str:
        return "na27" if "-secondary" in inputs.environment else "na26"


    def _setup_min_max_runners(self, inputs: WorkflowInputs) -> Tuple[int, int]:
        runners_with_large_inputs = [
            "im-linux",
            "im-ghas-linux",
            "im-image-builder"
        ]

        # More Complex Assignments
        max_runners = 10
        min_runners = 0
        if inputs.runner_name in runners_with_large_inputs:
            max_runners = 30
            min_runners = 1

        return min_runners, max_runners


    def _setup_annotation_runner_image_values(self, inputs: WorkflowInputs) -> str:
        annotation_runner_image = None
        if (
            not inputs.image or
            inputs.image.strip().lower() == "na" or
            inputs.image.strip() == ""
        ):
            tag = inputs.image_sha if inputs.image_sha and inputs.image_sha.strip().lower() != "na" else inputs.image_tag
            annotation_runner_image = f"{inputs.organization}/{inputs.runner_name}:{tag}"
        else:
            annotation_runner_image = f"{inputs.runner_name}:{inputs.image_tag}"

        return annotation_runner_image


    def _setup_runner_image_values(self, inputs: WorkflowInputs) -> str:
        runner_image = None
        if (
            not inputs.image or
            inputs.image.strip().lower() == "na" or
            inputs.image.strip() == ""
        ):
            runner_image = f"{inputs.registry}/{inputs.organization}/{inputs.runner_name}"
        else:
            runner_image = f"{inputs.registry}/{inputs.image}"

        return runner_image


    def _setup_listener_metadata_annotations(self, inputs: WorkflowInputs, prometheus_annotations: dict, annotation_runner_image: str) -> dict:
        listener_metadata_annotations = copy.copy(prometheus_annotations)
        listener_metadata_annotations["runnerImage"] = annotation_runner_image
        return listener_metadata_annotations


    def _setup_container_resources(self, inputs: WorkflowInputs, prometheus_annotations, annotation_runner_image: str):
        if inputs.platform == "linux":
            self.runner_metadata_annotations["runnerImage"] = annotation_runner_image
            self.runner_spec_containers_command = [
                "/home/runner/run.sh"
            ]
            self.runner_spec_containers_resources_limits_cpu = "1500m"
            self.runner_spec_containers_resources_limits_memory = "3Gi"
            self.runner_spec_containers_resources_requests_cpu = "100m"
            self.runner_spec_containers_resources_requests_memory = "200Mi"
            self.runner_spec_node_selector_agentpool = "linux"

        else:
            self.runner_metadata_annotations = copy.copy(prometheus_annotations)
            self.runner_metadata_annotations["runnerImage"] = annotation_runner_image
            self.runner_spec_containers_command = [
                "cmd.exe",
                "/c",
                "\\home\\runner\\run.cmd"
            ]
            self.runner_spec_containers_resources_limits_cpu = "3000m"
            self.runner_spec_containers_resources_limits_memory = "6Gi"
            self.runner_spec_containers_resources_requests_cpu = "500m"
            self.runner_spec_containers_resources_requests_memory = "2Gi"
            self.runner_spec_node_selector_agentpool = "windows"


    def _setup_runner_spec_container_image(self, inputs: WorkflowInputs, runner_image: str) -> str:
        runner_spec_containers_image = None
        if "sha256" in inputs.image_sha.lower():
            runner_spec_containers_image = f"{runner_image}@{inputs.image_sha}"
        else:
            runner_spec_containers_image = f"{runner_image}:{inputs.image_tag}"

        return runner_spec_containers_image


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

        if self.container_mode == "dind":
            helm_json["containerMode"] = {
                "type": "dind",
            }

        elif self.container_mode == "kubernetes":
            helm_json["containerMode"] = {
                "type": "kubernetes",
                "kubernetesModeWorkVolumeClaim" : {
                    "accessModes": [ "ReadWriteOnce" ],
                    "storageClassName": "dynamic-blob-storage",
                    "resources": {
                        "requests": {
                            "storage": self.container_kubernetes_resources_requests_storage_size
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




