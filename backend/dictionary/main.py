from loguru import logger
import uvicorn
from dictionary.webapp import app

if __name__ == "__main__":
    logger.info(f"Running app with proxy `{app.root_path}`")
    uvicorn.run(app, host="0.0.0.0", port=8000)
