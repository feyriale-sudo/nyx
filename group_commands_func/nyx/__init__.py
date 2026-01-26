from .ocs.create import create_oc_func
from .ocs.edit import edit_oc_func
from .ocs.remove import remove_oc_func
from .ocs.view import view_ocs_func
from .top_level.echo import echo_func
__all__ = [
    "echo_func",
    "create_oc_func",
    "edit_oc_func",
    "remove_oc_func",
    "view_ocs_func",
]
