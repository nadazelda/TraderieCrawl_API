from pydantic import BaseModel, Extra
from typing import List, Optional, Union

class Option(BaseModel):
    key: int
    min: Optional[int] = None
    max: Optional[int] = None
class ItemListRequest(BaseModel):
    kind: str

class ItemEntry(BaseModel):
    kind: str
    itemKey: str
    img: Optional[str]

class ItemRequest(BaseModel):
    ItemKey: Optional[str] = None
    ItemKinds: Optional[str] = None
    Options: Optional[List[Option]] = None
    items: Optional[List[ItemEntry]] = None
    options: Optional[List[Option]] = None
    prop_Ladder: Union[bool, str]
    prop_Mode: str
    prop_Ethereal: bool
    prop_Rarity: Optional[str] = None
    class Config:
        extra = Extra.allow  # ✅ 여기에 없는 필드도 받아들임
