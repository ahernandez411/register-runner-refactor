import copy
import os

from shared.static_values import StaticValues

class HelmDeployValues:
    def __init__(self) -> None:
        self.input_container_mode = os.getenv("CONTAINER_MODE", StaticValues.CONTAINER_MODE_NONE).lower()
        self.input_environment = os.getenv("TARGET_ENVIRONMENT", StaticValues.ENV_PROD).lower()
        self.input_image = os.getenv("IMAGE", None)
        self.input_image_sha = os.getenv("IMAGE_SHA", None)
        self.input_image_tag = os.getenv("IMAGE_TAG", None)
        self.input_organization = os.getenv("ORGANIZATION", None)
        self.input_platform = os.getenv("PLATFORM", StaticValues.PLATFORM_LINUX)
        self.input_registry = os.getenv("REGISTRY", None)
        self.input_runner_group = os.getenv("RUNNER_GROUP", None)
        self.input_runner_name = os.getenv("RUNNER_NAME", None)


    def create_helm_json(self) -> dict:
        # Hard-coded value assignments
        github_app_secret_name = "dynamic-runners-gh-app"
        controller_service_account_name = "im-arc-cntlr-gha-rs-controller"
        controller_service_account_namespace = "arc-system"
        prometheus_annotations = {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080",
            "prometheus.io/path": "/metrics",
        }
        listener_spec_containers_name = "listener"
        listener_spec_containers_resources_limits_cpu = "300m"
        listener_spec_containers_resources_limits_memory = "500Mi"
        listener_spec_containers_resources_requests_cpu = "100m"
        listener_spec_containers_resources_requests_memory = "128Mi"
        listener_spec_node_selector_agentpool = "mgmt"
        kubernetes_resources_requests_storage_size = "1Gi"
        runner_spec_containers_name = "runner"

        # Basic Assignment from environment variables
        github_config_url = f"https://github.com/{self.input_organization}"
        labels = {
            "org": self.input_organization,
            "region": "na27" if "-secondary" in self.input_environment else "na26"
        }
        listener_metadata_labels = copy.copy(labels)
        runner_metadata_labels = copy.copy(labels)
        runner_group = self.input_runner_group


        # More Complex Assignments
        max_runners = 0
        min_runners = 0
        if self.input_runner_name in StaticValues.RUNNERS_WITH_LARGE_LIMITS:
            max_runners = 30
            min_runners = 1
        else:
            max_runners = 10
            min_runners = 0

        runner_image = None
        annotation_runner_image = None
        if (
            not self.input_image or
            self.input_image.strip() == StaticValues.VALUE_NA or
            self.input_image.strip() == ""
        ):
            tag = self.input_image_sha if self.input_image_sha and self.input_image_sha.strip() != StaticValues.VALUE_NA else self.input_image_tag
            annotation_runner_image = f"{self.input_organization}/{self.input_runner_name}:{tag}"

            runner_image = f"{self.input_registry}/{self.input_organization}/{self.input_runner_name}"
        else:
            annotation_runner_image = f"{self.input_runner_name}:{self.input_image_tag}"
            runner_image = f"{self.input_registry}/{self.input_image}"

        listener_metadata_annotations = copy.copy(prometheus_annotations)
        listener_metadata_annotations["runnerImage"] = annotation_runner_image

        runner_spec_containers_image = None
        if "sha256" in self.input_image_sha.lower():
            runner_spec_containers_image = f"{runner_image}@{self.input_image_sha}"
        else:
            runner_spec_containers_image = f"{runner_image}:{self.input_image_tag}"

        runner_metadata_annotations = {}
        runner_spec_containers_command = []
        runner_spec_containers_resources_limits_cpu = ""
        runner_spec_containers_resources_limits_memory = ""
        runner_spec_containers_resources_requests_cpu = ""
        runner_spec_containers_resources_requests_memory = ""
        runner_spec_node_selector_agentpool = None
        if self.input_platform == StaticValues.PLATFORM_LINUX:
            runner_metadata_annotations["runnerImage"] = annotation_runner_image
            runner_spec_containers_command = [
                "/home/runner/run.sh"
            ]
            runner_spec_containers_resources_limits_cpu = "1500m"
            runner_spec_containers_resources_limits_memory = "3Gi"
            runner_spec_containers_resources_requests_cpu = "100m"
            runner_spec_containers_resources_requests_memory = "200Mi"
            runner_spec_node_selector_agentpool = StaticValues.PLATFORM_LINUX

        else:
            runner_metadata_annotations = copy.copy(prometheus_annotations)
            runner_metadata_annotations["runnerImage"] = annotation_runner_image
            runner_spec_containers_command = [
                "cmd.exe",
                "/c",
                "\\home\\runner\\run.cmd"
            ]
            runner_spec_containers_resources_limits_cpu = "3000m"
            runner_spec_containers_resources_limits_memory = "6Gi"
            runner_spec_containers_resources_requests_cpu = "500m"
            runner_spec_containers_resources_requests_memory = "2Gi"
            runner_spec_node_selector_agentpool = StaticValues.PLATFORM_WINDOWS

        helm_json = {
            "githubConfigUrl": github_config_url,
            "githubConfigSecret": github_app_secret_name,
            "maxRunners": max_runners,
            "minRunners": min_runners,
            "runnerGroup": runner_group,
            "controllerServiceAccount": {
                "name": controller_service_account_name,
                "namespace": controller_service_account_namespace,
            },
            "listenerTemplate": {
                "metadata": {
                    "annotations": listener_metadata_annotations,
                    "labels": listener_metadata_labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": listener_spec_containers_name,
                            "resources": {
                                "limits": {
                                    "cpu": listener_spec_containers_resources_limits_cpu,
                                    "memory": listener_spec_containers_resources_limits_memory,
                                },
                                "requests": {
                                    "cpu": listener_spec_containers_resources_requests_cpu,
                                    "memory": listener_spec_containers_resources_requests_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": listener_spec_node_selector_agentpool
                    }
                }
            },
            "template": {
                "metadata": {
                    "labels": runner_metadata_labels,
                    "annotations": runner_metadata_annotations,
                },
                "spec": {
                    "containers": [
                        {
                            "command": runner_spec_containers_command,
                            "name": runner_spec_containers_name,
                            "image": runner_spec_containers_image,
                            "resources": {
                                "limits": {
                                    "cpu": runner_spec_containers_resources_limits_cpu,
                                    "memory": runner_spec_containers_resources_limits_memory,
                                },
                                "requests": {
                                    "cpu": runner_spec_containers_resources_requests_cpu,
                                    "memory": runner_spec_containers_resources_requests_memory,
                                }
                            }
                        }
                    ],
                    "nodeSelector": {
                        "agentpool": runner_spec_node_selector_agentpool
                    }
                }
            }
        }

        if self.input_container_mode == StaticValues.CONTAINER_MODE_DIND:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_DIND,
            }

        elif self.input_container_mode == StaticValues.CONTAINER_MODE_KUBERNETES:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_KUBERNETES,
                "kubernetesModeWorkVolumeClaim" : {
                    "accessModes": [ "ReadWriteOnce" ],
                    "storageClassName": "dynamic-blob-storage",
                    "resources": {
                        "requests": {
                            "storage": kubernetes_resources_requests_storage_size
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




