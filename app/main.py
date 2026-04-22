from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from json import JSONDecodeError
from app.db.session import get_db
from app.models.github_event import GithubEvent
import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

logger = logging.getLogger("Github")

app = FastAPI()


# POST endpoint to recieve webhook
@app.post("/webhook")
async def get_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Access raw bytes - needed for HMAC verification
        raw_body = await request.body()

        hook_data = await request.json()
        event_type = request.headers.get("x-github-event")
        secret_header = request.headers.get("x-hub-signature-256")
        delivery_header = request.headers.get("X-GitHub-Delivery")

        github_event = GithubEvent(
            delivery_id=delivery_header, event_type=event_type, payload=hook_data
        )

        db.add(github_event)
        await db.commit()

        logger.info("Webhook recieved - event type: %s", event_type)

        return {"status": "received"}

    except JSONDecodeError as e:
        # Convert first 100 bytes of JSON to text string
        snip_bytes = raw_body[:100]
        snip_text = snip_bytes.decode("utf-8", errors="replace")
        logger.error("Invalid JSON recieved | Raw body: %s", snip_text)
        raise HTTPException(status_code=400, detail="Invalid JSON")

    except SQLAlchemyError as e:
        logger.error(
            "Database failure occured while saving event. Error Type: %s",
            type(e).__name__,
        )
        raise HTTPException(status_code=500, detail="Database failure")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
