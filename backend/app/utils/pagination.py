from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int = 20
    offset: int = 0

    @property
    def safe_limit(self) -> int:
        return max(1, min(self.limit, 100))

    @property
    def safe_offset(self) -> int:
        return max(0, self.offset)
