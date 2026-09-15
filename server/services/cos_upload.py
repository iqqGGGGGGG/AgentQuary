import logging
from qcloud_cos import CosConfig, CosS3Client
from config import settings

logger = logging.getLogger(__name__)

_client: CosS3Client | None = None


def _get_client() -> CosS3Client:
    global _client
    if _client is None:
        config = CosConfig(
            Region=settings.cos_region,
            SecretId=settings.cos_secret_id,
            SecretKey=settings.cos_secret_key,
        )
        _client = CosS3Client(config)
    return _client


def upload_image(image_bytes: bytes, key: str) -> str:
    try:
        client = _get_client()
        client.put_object(
            Bucket=settings.cos_bucket,
            Body=image_bytes,
            Key=key,
            ContentType="image/png",
        )
        url = f"https://{settings.cos_bucket}.cos.{settings.cos_region}.myqcloud.com/{key}"
        logger.debug("COS upload success: %s", url)
        return url
    except Exception as e:
        logger.error("COS upload failed: %s", e)
        raise
