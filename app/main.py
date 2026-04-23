from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from json import JSONDecodeError
from app.db.session import get_db
from app.models.github_event import GithubEvent
from app.security.verify import verify_signiture
from app.config import settings
import uvicorn
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

logger = logging.getLogger("Github")

app = FastAPI()


# POST endpoint to recieve webhook
@app.post("/webhook")
async def get_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Extract Raw body and Signiture header for HMAC verification
        raw_body = await request.body()
        secret_header = request.headers.get("x-hub-signature-256")

        # Verify signiture
        if not verify_signiture(raw_body, settings.github_secret, secret_header):
            logger.warning("Invalid signiture attempt")
            raise HTTPException(status_code=403, detail="Invalid signiture")

        hook_data = await request.json()
        event_type = request.headers.get("x-github-event")
        delivery_header = request.headers.get("X-GitHub-Delivery")

        # Store webhook data in db
        github_event = GithubEvent(
            delivery_id=delivery_header, event_type=event_type, payload=hook_data
        )

        db.add(github_event)
        await db.commit()

        logger.info(
            "Webhook recieved - ID: %s | event type: %s", delivery_header, event_type
        )

        return {"status": "received"}

    # Invalid JSON
    except JSONDecodeError:
        # Convert first 100 bytes to str and then log
        snip_bytes = raw_body[:100]
        snip_text = snip_bytes.decode("utf-8", errors="replace")
        logger.error(
            "Invalid JSON recieved - ID: %s | Raw body: %s", delivery_header, snip_text
        )
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Duplicate DB entry
    except IntegrityError:
        logger.info("Duplicate webhook ignored: %s", delivery_header)
        return {"status": "already_recieved"}

    # Other DB error
    except SQLAlchemyError as e:
        logger.error(
            "Database failure occured while saving event - ID: %s |  Error Type: %s",
            delivery_header,
            type(e).__name__,
        )
        raise HTTPException(status_code=500, detail="Database failure")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
