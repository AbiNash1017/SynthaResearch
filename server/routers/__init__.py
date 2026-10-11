from .system import router as system_router
from .experiments import router as experiments_router
from .personas import router as personas_router
from .surveys import router as surveys_router
from .interviews import router as interviews_router
from .reports import router as reports_router

__all__ = [
    "system_router",
    "experiments_router",
    "personas_router",
    "surveys_router",
    "interviews_router",
    "reports_router",
]
