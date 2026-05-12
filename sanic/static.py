import mimetypes
import os
from pathlib import Path, PurePath
from urllib.parse import unquote

from .errors import PathNotFound
from .response_types import ServerResponse


def guess_content_type(file_path, fallback="application/octet-stream"):
    media_type = mimetypes.guess_type(str(file_path))[0]
    if media_type is None:
        return fallback
    if media_type.startswith("text/") or media_type == "application/javascript":
        return f"{media_type}; charset=utf-8"
    return media_type


def _resolve_file(root, file_uri):
    root = Path(root).resolve()
    decoded = unquote(file_uri).lstrip("/")
    if not decoded:
        return root, True
    full = Path(root, decoded)

    for part in full.relative_to(root).parts:
        if part == "..":
            raise PathNotFound("Path traversal not allowed")

    resolved = full.resolve()

    try:
        resolved.relative_to(root)
    except ValueError:
        raise PathNotFound("Path outside root directory")

    return resolved, resolved.is_dir()


def _find_index(directory, index_names):
    if isinstance(index_names, str):
        index_names = [index_names]
    for name in index_names:
        candidate = Path(directory, name)
        if candidate.is_file():
            return candidate
    return None


def make_static_handler(file_or_directory, content_type=None, index=None):
    file_or_directory = str(file_or_directory)
    root = Path(file_or_directory).resolve()
    is_file_mode = root.is_file()

    async def handler(request, **kwargs):
        if is_file_mode:
            file_path = root
        else:
            file_uri = kwargs.get("__file_uri__", "")
            try:
                resolved, is_dir = _resolve_file(root, file_uri)
            except PathNotFound:
                raise PathNotFound(f"File not found")

            if is_dir:
                if index:
                    idx = _find_index(resolved, index)
                    if idx:
                        file_path = idx
                    else:
                        raise PathNotFound("File not found")
                else:
                    raise PathNotFound("File not found")
            else:
                if not resolved.is_file():
                    raise PathNotFound("File not found")
                file_path = resolved

        ct = content_type or guess_content_type(file_path)

        try:
            data = file_path.read_bytes()
        except (FileNotFoundError, PermissionError):
            raise PathNotFound("File not found")

        return ServerResponse(body=data, status=200, content_type=ct)

    return handler


def register_static(target, uri, file_or_directory, name="static",
                     content_type=None, index=None, strict_slashes=None):
    file_or_directory = str(file_or_directory)
    root = Path(file_or_directory)

    if root.is_file():
        handler = make_static_handler(file_or_directory,
                                      content_type=content_type)
        target.route(uri, methods=["GET", "HEAD"], name=name,
                     strict_slashes=strict_slashes)(handler)
    else:
        handler = make_static_handler(file_or_directory,
                                      content_type=content_type,
                                      index=index)
        pattern_uri = uri.rstrip("/") + "/<__file_uri__:path>"
        target.route(pattern_uri, methods=["GET", "HEAD"], name=name,
                     strict_slashes=strict_slashes)(handler)

        async def root_handler(request):
            return await handler(request, __file_uri__="")

        root_name = f"{name}_root"
        root_uri = uri.rstrip("/") or "/"
        target.route(root_uri, methods=["GET", "HEAD"], name=root_name,
                     strict_slashes=strict_slashes)(root_handler)
