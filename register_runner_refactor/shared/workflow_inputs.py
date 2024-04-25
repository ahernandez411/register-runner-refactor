import os

class WorkflowInputs:
    @property
    def runner_name(self):
        return os.getenv("RUNNER_NAME", None)

    @property
    def runner_group(self):
        return os.getenv("RUNNER_GROUP", None)

    @property
    def registry(self) -> str:
        return os.getenv("REGISTRY", None)

    @property
    def platform(self) -> str:
        return os.getenv("PLATFORM", "linux")

    @property
    def organization(self) -> str:
        return os.getenv("ORGANIZATION", None)

    @property
    def image_tag(self) -> str:
        return os.getenv("IMAGE_TAG", None)

    @property
    def image_sha(self):
        return os.getenv("IMAGE_SHA", None)

    @property
    def image(self) -> str:
        return os.getenv("IMAGE", None)

    @property
    def environment(self) -> str:
        return os.getenv("TARGET_ENVIRONMENT", "prod").lower()

    @property
    def container_mode(self) -> str:
        return os.getenv("CONTAINER_MODE", "none").lower()
