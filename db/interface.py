"""Legacy exports; new code imports from data.interfaces."""

from data.interfaces import HealthcheckAdapter, Repository, UnitOfWork

DatabaseAdapter = HealthcheckAdapter

__all__ = ["DatabaseAdapter", "Repository", "UnitOfWork"]
