
"""Legacy compatibility package for canonical Data interfaces."""

from .interface import DatabaseAdapter, Repository, UnitOfWork

__all__ = ["DatabaseAdapter", "Repository", "UnitOfWork"]
