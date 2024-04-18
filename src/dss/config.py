from enum import Enum

# Labels applied to any Kubernetes objects managed by the DSS CLI
DSS_CLI_MANAGER_LABELS = {"app.kubernetes.io/managed-by": "dss-cli"}

FIELD_MANAGER = "dss-cli"
DSS_NAMESPACE = "dss"
MANIFEST_TEMPLATES_LOCATION = "./manifest_templates"
MLFLOW_DEPLOYMENT_NAME = "mlflow"
NOTEBOOK_PVC_NAME = "notebooks"
NOTEBOOK_IMAGES_ALIASES = {
    "pytorch": "charmedkubeflow/jupyter-pytorch-full:1.8.0-3058193",
    # TODO: add the rest of the rocks once updated in https://github.com/canonical/kubeflow-rocks
    # "pytorch-cuda": "charmedkubeflow/jupyter-pytorch-cuda-full:1.8.0-xxxxx",
    # "tensorflow-cuda": "charmedkubeflow/jupyter-tensorflow-cuda-full:1.8.0-xxxx",
    # "tensorflow": "charmedkubeflow/jupyter-tensorflow-full:1.8.0-xxxx"
}
NOTEBOOK_LABEL = "canonical.com/dss-notebook"


def format_images_message(images_dict: dict) -> str:
    formatted_string = "Recommended images:\n"
    for key, value in images_dict.items():
        formatted_string += f"  - {key} = {value}\n"
    return formatted_string


RECOMMENDED_IMAGES_MESSAGE = format_images_message(NOTEBOOK_IMAGES_ALIASES)
DEFAULT_NOTEBOOK_IMAGE = "kubeflownotebookswg/jupyter-scipy:v1.8.0"


class DeploymentState(Enum):
    ACTIVE = "Active"
    DOWNLOADING = "Downloading"
    STARTING = "Starting"
    STOPPING = "Stopping"
    REMOVING = "Removing"
    STOPPED = "Stopped"
    UNKNOWN = "Unknown"
