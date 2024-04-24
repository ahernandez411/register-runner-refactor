import copy
import os

from shared.static_values import StaticValues

class HelmDeployValues:
    def __init__(self) -> None:
        self.container_mode = os.getenv("CONTAINER_MODE", StaticValues.CONTAINER_MODE_NONE).lower()
        self.environment = os.getenv("TARGET_ENVIRONMENT", StaticValues.ENV_PROD).lower()
        self.image = os.getenv("IMAGE", None)
        self.image_sha = os.getenv("IMAGE_SHA", None)
        self.image_tag = os.getenv("IMAGE_TAG", None)
        self.organization = os.getenv("ORGANIZATION", None)
        self.platform = os.getenv("PLATFORM", StaticValues.PLATFORM_LINUX)
        self.registry = os.getenv("REGISTRY", None)
        self.runner_group = os.getenv("RUNNER_GROUP", None)
        self.runner_name = os.getenv("RUNNER_NAME", None)


    def create_helm_json(self) -> dict:
        github_config_url = f"https://github.com/{self.organization}"
        github_app_secret_name = "dynamic-runners-gh-app"

        max_runners = 0
        min_runners = 0
        if self.runner_name in StaticValues.RUNNERS_WITH_LARGE_LIMITS:
            max_runners = 30
            min_runners = 1
        else:
            max_runners = 10
            min_runners = 0

        runner_group = self.runner_group

        controller_service_account_name = "im-arc-cntlr-gha-rs-controller"
        controller_service_account_namespace = "arc-system"

        annotation_runner_image = None
        runner_image = None
        if (
            not self.image or
            self.image.strip() == StaticValues.VALUE_NA or
            self.image.strip() == ""
        ):
            runner_image = f"{self.registry}/{self.organization}/{self.runner_name}"

            tag = None
            if self.image_sha and self.image_sha.strip() != StaticValues.VALUE_NA:
                tag = self.image_sha
            else:
                tag = self.image_tag

            annotation_runner_image = f"{self.organization}/{self.runner_name}:{tag}"
        else:
            runner_image = f"{self.registry}/{self.image}"
            annotation_runner_image = f"{self.runner_name}:{self.image_tag}"

        prometheus_annotations = {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080",
            "prometheus.io/path": "/metrics",
        }

        listener_metadata_annotations = copy.copy(prometheus_annotations)
        listener_metadata_annotations["runnerImage"] = annotation_runner_image

        labels = {
            "org": self.organization,
            "region": "na27" if "-secondary" in self.environment else "na26"
        }

        listener_metadata_labels = copy.copy(labels)

        listener_spec_containers_name = "listener"
        listener_spec_containers_resources_limits_cpu = "300m"
        listener_spec_containers_resources_limits_memory = "500Mi"
        listener_spec_containers_resources_requests_cpu = "100m"
        listener_spec_containers_resources_requests_memory = "128Mi"
        listener_spec_node_selector_agentpool = "mgmt"

        runner_metadata_labels = copy.copy(labels)
        runner_metadata_annotations = {}

        runner_spec_containers_command = []
        runner_spec_containers_name = "runner"

        runner_spec_containers_image = None
        if "sha256" in self.image_sha.lower():
            runner_spec_containers_image = f"{runner_image}@{self.image_sha}"
        else:
            runner_spec_containers_image = f"{runner_image}:{self.image_tag}"

        runner_spec_containers_resources_limits_cpu = ""
        runner_spec_containers_resources_limits_memory = ""
        runner_spec_containers_resources_requests_cpu = ""
        runner_spec_containers_resources_requests_memory = ""
        runner_spec_node_selector_agentpool = None
        if self.platform == StaticValues.PLATFORM_LINUX:
            runner_spec_containers_resources_requests_cpu = "100m"
            runner_spec_containers_resources_requests_memory = "200Mi"
            runner_spec_containers_resources_limits_cpu = "1500m"
            runner_spec_containers_resources_limits_memory = "3Gi"
            runner_spec_node_selector_agentpool = StaticValues.PLATFORM_LINUX
            runner_spec_containers_command = [
                "/home/runner/run.sh"
            ]
            runner_metadata_annotations["runnerImage"] = annotation_runner_image
        else:
            runner_spec_containers_resources_requests_cpu = "500m"
            runner_spec_containers_resources_requests_memory = "2Gi"
            runner_spec_containers_resources_limits_cpu = "3000m"
            runner_spec_containers_resources_limits_memory = "6Gi"
            runner_spec_node_selector_agentpool = StaticValues.PLATFORM_WINDOWS
            runner_spec_containers_command = [
                "cmd.exe",
                "/c",
                "\\home\\runner\\run.cmd"
            ]
            runner_metadata_annotations = copy.copy(prometheus_annotations)
            runner_metadata_annotations["runnerImage"] = annotation_runner_image

        kubernetes_resources_requests_storage = ""

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

        if self.container_mode == StaticValues.CONTAINER_MODE_DIND:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_DIND,
            }

        elif self.container_mode == StaticValues.CONTAINER_MODE_KUBERNETES:
            helm_json["containerMode"] = {
                "type": StaticValues.CONTAINER_MODE_KUBERNETES,
                "kubernetesModeWorkVolumeClaim" : {
                    "accessModes": [ "ReadWriteOnce" ],
                    "storageClassName": "dynamic-blob-storage",
                    "resources": {
                        "requests": {
                            "storage": kubernetes_resources_requests_storage
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




