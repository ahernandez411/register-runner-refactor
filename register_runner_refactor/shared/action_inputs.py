from shared.config_builder_deploy_values import ConfigBuilderDeployValues

class ActionInputs:
    def __init__(self) -> None:
        self.default_inputs_image_sha = "NA"
        self.default_inputs_use_hosted_runners = False
        self.default_runners_with_large_limits = [
            "im-linux",
            "im-ghas-linux",
            "im-image-builder"
        ]

        self.options_inputs_environment = [
            "dev",
            "dev-secondary",
            "prod",
            "prod-secondary",
        ]
        self.option_inputs_platform_linux = "linux"
        self.option_inputs_platform_windows = "windows"
        self.options_inputs_platform = [
            "linux",
            "windows",
        ]
        self.options_inputs_container_mode = [
            "none",
            "dind",
            "kubernetes",
        ]
        self.options_inputs_organization = [
            "im-client",
            "im-customer-engagement",
            "im-enrollment",
            "im-funding",
            "im-platform",
            "im-practices"
        ]
        self.options_inputs_action = [
            "Register",
            "Delete",
            "Uninstall-Only"
        ]

        self.env_github_ref = "" #"main"

        self.github_ref_name = "" #"main"
        self.github_sha = "" #"1d56d71bcf81ae3b85a63281d31f86501185d24e"

        self.inputs_action = "" #"register"
        self.inputs_container_mode = "" #"none"
        self.inputs_environment = "" #"prod"
        self.inputs_image = "" #"NA"
        self.inputs_image_sha = "" #"NA"
        self.inputs_image_tag = "" #"ubuntu-22.04"
        self.inputs_organization = "" #"im-platform"
        self.inputs_platform = "" #"linux"
        self.inputs_runner_name = "" #"aric-dotnet"
        self.inputs_use_hosted_runners = False #"false"

        self.needs_set_vars_outputs_registry = ""

        self.steps_get_runner_name_outputs_runner_full_name = ""
        self.steps_get_runner_name_outputs_runner_group = ""
        self.steps_get_runner_name_outputs_runner_name = ""

        self.steps_set_variables_outputs_cluster_name = "" #"BDAIM-P-NA26-DynamicRunners-K8S"
        self.steps_set_variables_outputs_runs_on = "" #"dyn-im-image-builder"
        self.steps_set_variables_outputs_target_resource_group = "" #"BDAIM-P-NA26-DynamicRunners-RGRP"


    def create_config_builder_deploy_values(self) -> ConfigBuilderDeployValues:
        instance = ConfigBuilderDeployValues()

        instance.runner_group = self.steps_get_runner_name_outputs_runner_group
        instance.runner_tag = self.inputs_image_tag
        instance.runner_sha = self.inputs_image_sha
        instance.github_config_url = f"https://github.com/{self.inputs_organization}"
        instance.github_app_secret_name = "dynamic-runners-gh-app"
        instance.listener_max_cpu = "300m"
        instance.listener_max_memory = "500Mi"
        instance.listener_agent_pool = "mgmt"
        instance.controller_service_account_name = "im-arc-cntlr-gha-rs-controller"
        instance.controller_service_account_namespace = "arc-system"
        instance.container_mode = self.inputs_container_mode

        if self.inputs_platform == self.option_inputs_platform_linux:
            instance.runner_request_cpu = "100m"
            instance.runner_request_memory = "200Mi"
            instance.runner_max_cpu = "1500m"
            instance.runner_max_memory = "3Gi"
            instance.runner_agent_pool = self.option_inputs_platform_linux
            instance.runner_command = [
                "/home/runner/run.sh"
            ]
        else:
            instance.runner_request_cpu = "500m"
            instance.runner_request_cpu = "2Gi"
            instance.runner_max_cpu = "3000m"
            instance.runner_max_memory = "6Gi"
            instance.runner_agent_pool = self.option_inputs_platform_windows
            instance.runner_command = [
                "cmd.exe",
                "/c",
                "\\home\\runner\\run.cmd"
            ]

        instance.labels = {
            "org": self.inputs_organization,
            "region": "na27" if "-secondary" in self.inputs_environment else "na26"
        }

        if not self.inputs_image or self.inputs_image.strip() == "NA" or self.inputs_image.strip() == "":
            instance.runner_image = f"{self.needs_set_vars_outputs_registry}/{self.inputs_organization}/{self.steps_get_runner_name_outputs_runner_name}"
            tag = self.inputs_image_sha if self.inputs_image_sha and self.inputs_image_sha.strip() != "NA" else self.inputs_image_tag

            instance.annotations = {
                "runnerImage": f"{self.inputs_organization}/{self.steps_get_runner_name_outputs_runner_name}:{tag}"
            }
        else:
            instance.runner_image = f"{self.needs_set_vars_outputs_registry}/{self.inputs_image}"
            instance.annotations = {
                "runnerImage": f"{self.inputs_image}:{self.inputs_image_tag}"
            }

        if self.steps_get_runner_name_outputs_runner_name in self.default_runners_with_large_limits:
            instance.max_runners = 30
            instance.min_runners = 1
        else:
            instance.max_runners = 10
            instance.min_runners = 0

        return instance





