class StaticValues:
    ACTION_DELETE = "Delete"
    ACTION_REGISTER = "Register"
    ACTION_UNINSTALL_ONLY = "Uninstall-Only"

    CONTAINER_MODE_DIND = "dind"
    CONTAINER_MODE_KUBERNETES = "kubernetes"
    CONTAINER_MODE_NONE = "none"

    ENV_DEV = "dev"
    ENV_DEV_SECONDARY = "dev-secondary"
    ENV_PROD = "prod"
    ENV_PROD_SECONDARY = "prod-secondary"

    VALUE_NA = "NA"

    ORG_CLIENT = "im-client"
    ORG_CUSTOMER_ENGAGEMENT = "im-customer-engagement"
    ORG_ENROLLMENT = "im-enrollment"
    ORG_FUNDING = "im-funding"
    ORG_PLATFORM = "im-platform"
    ORG_PRACTICES = "im-practices"

    PLATFORM_LINUX = "linux"
    PLATFORM_WINDOWS = "windows"

    RUNNERS_WITH_LARGE_LIMITS = [
        "im-linux",
        "im-ghas-linux",
        "im-image-builder"
    ]

    USE_HOSTED_RUNNERS_FALSE = False



