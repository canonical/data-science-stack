from enum import Enum

# Labels applied to any Kubernetes objects managed by the DSS CLI
DSS_CLI_MANAGER_LABELS = {"app.kubernetes.io/managed-by": "dss-cli"}

FIELD_MANAGER = "dss-cli"
DSS_NAMESPACE = "dss"
MANIFEST_TEMPLATES_LOCATION = "./manifest_templates"
MLFLOW_DEPLOYMENT_NAME = "mlflow"
NOTEBOOK_PVC_NAME = "notebooks"
NOTEBOOK_IMAGES_ALIASES = {
    "pytorch": "kubeflownotebookswg/jupyter-pytorch-full:v1.8.0",
    "pytorch-cuda": "kubeflownotebookswg/jupyter-pytorch-cuda-full:v1.8.0",
    "tensorflow-cuda": "kubeflownotebookswg/jupyter-tensorflow-cuda-full:v1.8.0",
    "tensorflow": "kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0"
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
    NO_SERVICE = "No service"
    REMOVING = "Removing"
    STARTING = "Starting"
    STOPPED = "Stopped"
    STOPPING = "Stopping"
    UNKNOWN = "Unknown"
