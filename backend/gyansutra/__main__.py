import os

import uvicorn

from .config import integer

if __name__ == "__main__":
    uvicorn.run(
        "gyansutra.app:app",
        host="0.0.0.0",
        port=integer("PORT", 3001, 0, 65535),
        reload=os.getenv("NODE_ENV") == "development",
        proxy_headers=False,
        workers=1,
    )
