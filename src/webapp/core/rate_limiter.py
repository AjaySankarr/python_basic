# from slowapi import Limiter 
# from slowapi.util import get_remote_address

# limiter = Limiter(
#     key_func = get_remote_address
# )


from slowapi import Limiter
from slowapi.util import get_remote_address

from webapp.core.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    headers_enabled=True
)