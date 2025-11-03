"""Lightweight Typer compatibility layer used for the CLI test-suite.

This module implements a very small subset of the public :mod:`typer`
interface that the repository relies on.  The real Typer project is a thin
wrapper around Click.  Instead of pulling the external dependency into the
execution environment we re-implement the pieces that are needed for the unit
tests by delegating to :mod:`click` directly.

Only the following capabilities are covered:

* ``Typer`` application container with ``command`` and ``callback`` helpers.
* ``Option`` factory used as default values inside command functions.
* ``Context`` object, ``echo``/``secho`` helpers and ``prompt`` for interactive
  questions.
* Exceptions and colour constants that the CLI surfaces rely on.
* ``typer.testing.CliRunner`` which proxies to :mod:`click.testing`.

The goal is to provide enough behaviour for our commands and tests to run
without shipping the full Typer dependency.  The implementation purposefully
keeps the surface area small and raises informative errors if unsupported
features are requested.
"""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from pathlib import Path
from importlib import import_module
from typing import Any, Callable, Iterable, Optional, Sequence, Union

import click

__all__ = [
    "Typer",
    "Context",
    "Option",
    "BadParameter",
    "Exit",
    "colors",
    "echo",
    "secho",
    "prompt",
    "testing",
]


Context = click.Context


class colors:
    """Minimal colour constants compatible with :mod:`typer.colors`."""

    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"


echo = click.echo
secho = click.secho
prompt = click.prompt


BadParameter = click.BadParameter
Exit = click.exceptions.Exit


@dataclass
class _OptionInfo:
    """Internal data structure representing a CLI option."""

    default: Any
    param_decls: Sequence[str]
    kwargs: dict[str, Any]


def Option(default: Any = ..., *names: str, **kwargs: Any) -> _OptionInfo:
    """Return a descriptor capturing option metadata.

    ``typer.Option`` is usually used as a default value in function
    signatures.  When commands are registered we translate the descriptor into
    Click option decorators.
    """

    return _OptionInfo(default=default, param_decls=names, kwargs=kwargs)


def _resolve_annotation(annotation: Any) -> Any:
    """Translate typing annotations into Click compatible types."""

    if isinstance(annotation, str):
        return {
            "bool": bool,
            "int": int,
            "float": float,
            "str": str,
            "Path": Path,
        }.get(annotation, str)

    try:  # Python 3.8+: typing.get_origin / get_args
        from typing import get_args, get_origin
    except ImportError:  # pragma: no cover - fallback for older Python
        return str

    origin = get_origin(annotation)
    if origin is None:
        return annotation

    if origin in (Optional, Union):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]  # noqa: E721
        return args[0] if args else str

    return str


def _decorate_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply Click option decorators based on :func:`Option` defaults."""

    signature = inspect.signature(func)
    callback = func

    for name, parameter in reversed(list(signature.parameters.items())):
        default = parameter.default
        if isinstance(default, _OptionInfo):
            option = default
            option_kwargs = dict(option.kwargs)
            decls: Iterable[str]
            if option.param_decls:
                decls = option.param_decls
            else:
                decls = (f"--{name.replace('_', '-')}",)

            parameter_type = _resolve_annotation(parameter.annotation)
            if parameter_type in (bool, click.BOOL):
                option_kwargs.setdefault("is_flag", True)
            else:
                if parameter_type not in (inspect.Signature.empty, None):
                    if parameter_type in (int, float, str):
                        option_kwargs.setdefault("type", parameter_type)

            path_flags = {
                key: option_kwargs.pop(key)
                for key in list(option_kwargs.keys())
                if key
                in {
                    "exists",
                    "file_okay",
                    "dir_okay",
                    "writable",
                    "readable",
                    "resolve_path",
                    "allow_dash",
                    "path_type",
                }
            }
            if parameter_type is Path or path_flags:
                path_flags.setdefault("path_type", Path)
                option_kwargs.setdefault("type", click.Path(**path_flags))

            if option.default is ...:
                option_kwargs.setdefault("required", True)
            else:
                option_kwargs.setdefault("default", option.default)

            callback = click.option(*decls, **option_kwargs)(callback)

    return callback


def _inject_context(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap callbacks so that a :class:`click.Context` is passed when needed."""

    signature = inspect.signature(func)
    needs_context = any(
        param.annotation is Context
        or (isinstance(param.annotation, str) and param.annotation in {"Context", "typer.Context"})
        for param in signature.parameters.values()
    )

    if needs_context:
        return click.pass_context(func)
    return func


class Typer:
    """Subset of Typer's API backed by :class:`click.Group`."""

    def __init__(self, *, help: str | None = None, name: str | None = None) -> None:
        self.name = name or "aion"
        self._group = click.Group(name=self.name, help=help)
        self._callback: Callable[..., Any] | None = None

    def command(
        self,
        name: str | None = None,
        *,
        help: str | None = None,
        context_settings: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a command callback."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            callback = _decorate_options(func)
            callback = _inject_context(callback)
            command_name = name or func.__name__.replace("_", "-")
            command = click.command(
                command_name,
                help=help,
                context_settings=context_settings,
            )(callback)
            self._group.add_command(command)
            return command

        return decorator

    def callback(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a group-level callback."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            callback = _decorate_options(func)
            callback = _inject_context(callback)
            self._callback = callback  # stored for potential manual invocation
            return callback

        return decorator

    def add_typer(self, sub_app: "Typer", *, name: str | None = None) -> None:
        if not isinstance(sub_app, Typer):  # pragma: no cover - defensive
            raise TypeError("add_typer expects a Typer instance")
        command_name = name or sub_app._group.name or sub_app._group.help or "command"
        self._group.add_command(sub_app._group, command_name)

    def __call__(self, args: Sequence[str] | None = None) -> None:
        self._group.main(
            args=list(args) if args is not None else None,
            standalone_mode=False,
            prog_name=self.name,
        )

    def main(self, args: Sequence[str] | None = None, **extra: Any) -> None:
        """Compatibility wrapper invoked by :class:`click.testing.CliRunner`."""

        return self.__call__(args=args)


testing = import_module(__name__ + ".testing")
globals()["testing"] = testing

