from .echo import router as echo_router
from .banking import router as banking_router
from .finance import router as finance_router

routers = [echo_router, banking_router, finance_router] 