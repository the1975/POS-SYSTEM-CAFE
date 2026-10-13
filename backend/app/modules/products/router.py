"""Endpoint menu untuk customer (publik, tanpa login). CRUD admin menyusul bersama RBAC."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.responses import DataResponse, PageResponse
from app.modules.products.dependencies import get_menu_service
from app.modules.products.schema import CategoryOut, ProductOut, ProductSort
from app.modules.products.service import MenuService

router = APIRouter(tags=["menu"])
ServiceDep = Annotated[MenuService, Depends(get_menu_service)]


@router.get("/categories", response_model=DataResponse[list[CategoryOut]])
def list_categories(service: ServiceDep):
    return DataResponse(data=service.list_categories())


@router.get("/categories/{category_id}", response_model=DataResponse[CategoryOut])
def get_category(category_id: uuid.UUID, service: ServiceDep):
    return DataResponse(data=service.get_category(category_id))


@router.get("/products", response_model=PageResponse[ProductOut])
def list_products(
    service: ServiceDep,
    category_id: uuid.UUID | None = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
    sort: ProductSort = ProductSort.NAME,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_products(
        category_id=category_id, search=search, sort=sort, page=page, page_size=page_size
    )
    return PageResponse(data=items, pagination=pagination)


@router.get("/products/{product_id}", response_model=DataResponse[ProductOut])
def get_product(product_id: uuid.UUID, service: ServiceDep):
    return DataResponse(data=service.get_product(product_id))
