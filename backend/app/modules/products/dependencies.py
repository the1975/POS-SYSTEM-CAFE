from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.products.repository import MenuRepository
from app.modules.products.service import MenuService


def get_menu_service(db: Annotated[Session, Depends(get_db)]) -> MenuService:
    return MenuService(MenuRepository(db))
