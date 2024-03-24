from dataclasses import dataclass
from io import BytesIO
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, Session, mapped_column
from v2.commands.images.models.image_mod import ImageMod
from v2.confs.envs_conf import envs_conf_impl
from v2.confs.sqlalchemy_conf import sqlalchemy_conf_impl
from v2.queries.app.models.card_download_mod import CardDownloadMod


class CardDownloadRow(sqlalchemy_conf_impl.Base):
    __tablename__ = "card_downloads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[dict[str, Any]] = mapped_column(type_=JSON, nullable=False)
    image_id: Mapped[int] = mapped_column(unique=True, index=True)

    @classmethod
    def insert_with(cls, session: Session, mod: CardDownloadMod) -> None:
        row = CardDownloadRow(data=mod.model_dump(), image_id=mod.image_id)
        session.add(row)

    def update_with(self, mod: CardDownloadMod) -> None:
        self.data = mod.model_dump()
        self.image_id = mod.image_id

    def to_mod(self) -> CardDownloadMod:
        return CardDownloadMod.model_validate(self.data)


@dataclass
class CardDownloadsRep:
    envs_conf = envs_conf_impl

    def get(self, session: Session, image_id: int) -> CardDownloadMod:
        return (
            session.query(CardDownloadRow)
            .where(CardDownloadRow.image_id == image_id)
            .one()
            .to_mod()
        )

    def sync(self, session: Session, image: ImageMod) -> None:
        def build_bytes() -> "bytes":
            bytesio = BytesIO()
            image.data.save(bytesio, image.extension().value)
            bytesio.seek(0)
            return bytesio.getvalue()

        bytes = build_bytes()
        mod = CardDownloadMod(
            bytes=bytes,
            media_type=image.extension().to_media_type(),
            filename=f"{image.name}.{image.extension().to_file_extension()}",
            image_id=image.id,
        )
        row = (
            session.query(CardDownloadRow)
            .where(CardDownloadRow.image_id == image.id)
            .one_or_none()
        )
        row.update_with(mod) if row else CardDownloadRow.insert_with(session, mod)

    def clean_sync(self, session: Session, image_id: int) -> None:
        session.query(CardDownloadRow).where(
            CardDownloadRow.image_id == image_id
        ).delete()


card_downloads_rep_impl = CardDownloadsRep()
