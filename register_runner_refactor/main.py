import json

from shared.action_inputs import ActionInputs
from shared.config_builder_deploy_values import ConfigBuilderDeployValues

class Main:
    def __init__(self) -> None:
        self.path_example_output = "temp/dyn-aric-dotnet.values.json"
        self.path_compare = "temp/compare"


    def run(self):
        # | Deploy Arguments          | Value                    |
        # | ---                       |  ---                     |
        # | Environment               | `${{ inputs.environment }}` |
        # | Action                    | `${{ inputs.action }}` |
        # | Branch Tag                | `${{ env.GITHUB_REF  }}`  |
        # | Cluster Name              | `${{ steps.set-variables.outputs.CLUSTER_NAME }}` |
        # | Target Resource Group     | `${{ steps.set-variables.outputs.TARGET_RESOURCE_GROUP }}` |
        # | Runner Name               | `${{ inputs.runner-name }}` |
        # | Image                     | `${{ inputs.image == 0 && 'NA' || inputs.image }}` |
        # | Organization              | `${{ inputs.organization }}` |
        # | Config Version / Image Tag | `${{ inputs.image-tag }}` |
        # | Image SHA                 | `${{ inputs.image-sha }}` |
        # | Constainer Mode           | `${{ inputs.container-mode }}` |
        # | Platform                  | `${{ inputs.platform }}` |
        # | Runs On                   | `${{ steps.set-variables.outputs.RUNS_ON }}`  |
        # | Use Hosted Runners        | `${{ inputs.use-hosted-runner }}` |
        # | Workflow Branch/Tag       | `${{ github.ref_name }}` - SHA: `${{ github.sha }}` |' >> $GITHUB_STEP_SUMMARY
        inputs_environment = "prod"
        inputs_action = "register"
        env_github_ref = "main"
        steps_set_variables_outputs_cluster_name = "BDAIM-P-NA26-DynamicRunners-K8S"
        steps_set_variables_outputs_target_resource_group = "BDAIM-P-NA26-DynamicRunners-RGRP"
        inputs_runner_name = "aric-dotnet"
        inputs_image = "NA"
        inputs_organization = "im-platform"
        inputs_image_tag = "ubuntu-22.04"
        inputs_image_sha = "NA"
        inputs_container_mode = "none"
        inputs_platform = "linux"
        steps_set_variables_outputs_runs_on = "dyn-im-image-builder"
        inputs_use_hosted_runners = False
        github_ref_name = "main"
        github_sha = "1d56d71bcf81ae3b85a63281d31f86501185d24e"

        registry = "dynamicrunnersprodcr.azurecr.io"
        runner_full_name = "aric-dotnet"
        runner_group = "dynamic-runners"
        runner_name = "aric-dotnet"

        action_inputs = ActionInputs()
        action_inputs.env_github_ref = env_github_ref
        action_inputs.github_ref_name = github_ref_name
        action_inputs.github_sha = github_sha
        action_inputs.inputs_action = inputs_action
        action_inputs.inputs_container_mode = inputs_container_mode
        action_inputs.inputs_environment = inputs_environment
        action_inputs.inputs_image = inputs_image
        action_inputs.inputs_image_sha = inputs_image_sha
        action_inputs.inputs_image_tag = inputs_image_tag
        action_inputs.inputs_organization = inputs_organization
        action_inputs.inputs_platform = inputs_platform
        action_inputs.inputs_runner_name = inputs_runner_name
        action_inputs.inputs_use_hosted_runners = inputs_use_hosted_runners
        action_inputs.steps_set_vars_outputs_cluster_name = steps_set_variables_outputs_cluster_name
        action_inputs.steps_set_vars_outputs_runs_on = steps_set_variables_outputs_runs_on
        action_inputs.steps_set_vars_outputs_target_resource_group = steps_set_variables_outputs_target_resource_group

        action_inputs.needs_set_vars_outputs_registry = registry
        action_inputs.steps_get_runner_name_outputs_runner_full_name = runner_full_name
        action_inputs.steps_get_runner_name_outputs_runner_group = runner_group
        action_inputs.steps_get_runner_name_outputs_runner_name = runner_name

        deploy_values = action_inputs.create_config_builder_deploy_values()
        values_json = deploy_values.create_values_json()
        self._save_results("generated-values", values_json)

        example_output = self._load_example_output()
        self._save_results("example-output", example_output)


    def _save_results(self, name: str, results: dict):
        with open(f"{self.path_compare}/{name}.json", "w") as writer:
            json.dump(results, writer, indent=3, sort_keys=True)


    def _load_example_output(self) -> dict:
        with open(self.path_example_output, "r") as reader:
            return json.load(reader)







if __name__ == "__main__":
    main = Main()
    main.run()
