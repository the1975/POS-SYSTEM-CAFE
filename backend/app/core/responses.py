"""Envelope response standar (api-design.md §8). Dipakai semua endpoint sukses."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class DataResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str | None = None


class PageResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    pagination: Pagination


def build_pagination(page: int, page_size: int, total: int) -> Pagination:
    # ceil tanpa import math; total 0 -> 0 halaman.
    return Pagination(
        page=page, page_size=page_size, total=total, total_pages=-(-total // page_size)
    )
