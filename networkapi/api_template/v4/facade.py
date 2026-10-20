# -*- coding: utf-8 -*-
import logging
import os

from networkapi.api_template.v4 import exceptions
from networkapi.settings import CONFIG_TEMPLATE_PATH
from networkapi.system.facade import get_value as get_variable

log = logging.getLogger(__name__)

TEMPLATE_TYPES = ('config', 'rack')


def _get_variable_or_default(name, default=None):
    try:
        return get_variable(name) or default
    except Exception:
        return default


def get_template_root(template_type):
    """Returns the root directory where templates of a type are stored.

    - config: CONFIG_TEMPLATE_PATH (with interface, network, bgp
      subdirectories).
    - rack: variable `path_to_guide`, as done in api_rack provision.
    """

    if template_type == 'config':
        return CONFIG_TEMPLATE_PATH

    if template_type == 'rack':
        return _get_variable_or_default('path_to_guide')

    return None


def _validate_path(file_path):
    """Allows only plain relative paths: no absolute paths, backslashes,
    null bytes or empty, `.` and `..` segments.
    """

    if not file_path or '\x00' in file_path or '\\' in file_path or \
            os.path.isabs(file_path):
        raise exceptions.InvalidTemplatePathException(file_path)

    for segment in file_path.split('/'):
        if segment in ('', '.', '..'):
            raise exceptions.InvalidTemplatePathException(file_path)


def _resolve_file(directory, file_path):
    """Returns the real path of file_path inside directory or None.

    Paths leaving the directory (path traversal) are rejected.
    """

    _validate_path(file_path)

    if not directory or not os.path.isdir(directory):
        return None

    base = os.path.realpath(directory)
    filename = os.path.realpath(os.path.join(base, file_path))

    if not filename.startswith(base + os.sep):
        raise exceptions.InvalidTemplatePathException(file_path)

    if not os.path.isfile(filename):
        return None

    return filename


def get_template_content(template_type, file_path):
    """Returns the exact content of a template.

    :param template_type: Template type (config, rack).
    :param file_path: Template path relative to the root directory of the
        type, e.g. `bgp/template_neighbor_v4_remove_junos`.
    """

    if template_type not in TEMPLATE_TYPES:
        raise exceptions.InvalidTemplateTypeException(template_type)

    filename_path = _resolve_file(get_template_root(template_type), file_path)
    if not filename_path:
        raise exceptions.TemplateNotFoundException(file_path)

    try:
        with open(filename_path, 'r') as file_handle:
            return file_handle.read()
    except IOError:
        log.exception('Error reading template file: %s', filename_path)
        raise exceptions.TemplateReadException(file_path)
