"""
Resolve a list of dependencies via the `resolvelib` API as well as a custom
`Resolver` that uses PyPI as an information source.
"""

from typing import List, Optional

from packaging.requirements import Requirement
from requests.exceptions import HTTPError
from resolvelib import BaseReporter, Resolver

from pip_audit._dependency_source import DependencyResolver, DependencyResolverError
from pip_audit._service.interface import ResolvedDependency
from pip_audit._state import AuditState

from .pypi_provider import PyPIProvider


class ResolveLibResolver(DependencyResolver):
    """
    An implementation of `DependencyResolver` that uses `resolvelib` as its
    backend dependency resolution strategy.
    """

    def __init__(self, timeout: Optional[int] = None, state: Optional[AuditState] = None) -> None:
        """
        Create a new `ResolveLibResolver`.

        `state` is an optional `AuditState` to use for state callbacks.
        """
        self.provider = PyPIProvider(timeout, state)
        self.reporter = BaseReporter()
        self.resolver: Resolver = Resolver(self.provider, self.reporter)

    def resolve(self, req: Requirement) -> List[ResolvedDependency]:
        """
        Resolve the given `Requirement` into a `Dependency` list.
        """
        deps: List[ResolvedDependency] = []
        try:
            result = self.resolver.resolve([req])
        except HTTPError as e:
            raise ResolveLibResolverError("failed to resolve dependencies") from e
        for name, candidate in result.mapping.items():
            deps.append(ResolvedDependency(name, candidate.version))
        return deps


class ResolveLibResolverError(DependencyResolverError):
    """
    A `resolvelib`-specific `DependencyResolverError`.
    """

    pass
