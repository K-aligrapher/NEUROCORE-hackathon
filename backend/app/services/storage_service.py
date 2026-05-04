import io
import uuid
from typing import Optional, BinaryIO
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from app.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Created bucket", bucket=self.bucket)
        except S3Error as e:
            logger.error("Bucket error", error=str(e))

    def upload_file(
        self, data: bytes, object_name: str, content_type: str = "application/octet-stream"
    ) -> str:
        try:
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            logger.info("Uploaded file", object_name=object_name)
            return object_name
        except S3Error as e:
            logger.error("Upload error", error=str(e))
            raise

    def upload_image(
        self, data: bytes, job_id: str, folder: str = "original"
    ) -> str:
        object_name = f"images/{folder}/{job_id}.jpg"
        return self.upload_file(data, object_name, "image/jpeg")

    def upload_cell_crop(
        self, data: bytes, job_id: str, cell_index: int
    ) -> str:
        object_name = f"cells/crops/{job_id}/{cell_index}.png"
        return self.upload_file(data, object_name, "image/png")

    def upload_heatmap(
        self, data: bytes, job_id: str, cell_index: int, disease: str
    ) -> str:
        object_name = f"cells/heatmaps/{job_id}/{cell_index}_{disease}.png"
        return self.upload_file(data, object_name, "image/png")

    def upload_annotated(
        self, data: bytes, job_id: str
    ) -> str:
        object_name = f"images/annotated/{job_id}.jpg"
        return self.upload_file(data, object_name, "image/jpeg")

    def upload_thumbnail(
        self, data: bytes, job_id: str
    ) -> str:
        object_name = f"images/thumbnails/{job_id}.jpg"
        return self.upload_file(data, object_name, "image/jpeg")

    def upload_report(
        self, data: bytes, job_id: str
    ) -> str:
        object_name = f"reports/{job_id}/report.pdf"
        return self.upload_file(data, object_name, "application/pdf")

    def get_file(self, object_name: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error:
            return None

    def get_presigned_url(
        self, object_name: str, expires_seconds: int = 3600
    ) -> Optional[str]:
        try:
            url = self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except S3Error:
            return None

    def delete_file(self, object_name: str) -> bool:
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    def delete_job_files(self, job_id: str) -> bool:
        try:
            objects_to_delete = [
                f"images/original/{job_id}.jpg",
                f"images/annotated/{job_id}.jpg",
                f"images/thumbnails/{job_id}.jpg",
                f"reports/{job_id}/report.pdf",
            ]
            for obj in objects_to_delete:
                try:
                    self.client.remove_object(self.bucket, obj)
                except S3Error:
                    pass
            return True
        except Exception:
            return False


storage_service = StorageService()


def get_storage() -> StorageService:
    return storage_service