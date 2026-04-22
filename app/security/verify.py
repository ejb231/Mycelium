import hashlib
import hmac


def verify_signiture(payload_body: bytes, secret: str, recieved_signiture: str) -> bool:

    computed = hmac.new(
        key=secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )

    expected_signiture = f"sha1:{computed}"

    return hmac.compare_digest(recieved_signiture, expected_signiture)
