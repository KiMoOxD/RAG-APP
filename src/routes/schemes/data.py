from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100  # Default chunk size is 100kb
    overlap: Optional[int] = 20  # Default overlap is 20 seconds
    do_reset: Optional[int] = 0  # Default is False, meaning do not reset the state

