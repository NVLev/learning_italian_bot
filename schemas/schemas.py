from typing import List

from pydantic import BaseModel, ConfigDict

class ThemeBase(BaseModel):
    name: str

    # config = ConfigDict(from_attributes=True)

class ThemeCreate(ThemeBase):
    pass

class ThemeRead(ThemeBase):
    id: int
    name: str

class VocabularyBase(BaseModel):
    italian_word: str
    rus_word: str

    # config = ConfigDict(from_attributes=True)

class VocabularyCreate(VocabularyBase):
    pass

class VocabularyRead(VocabularyBase):
    italian_word: str
    rus_word: str

class IdiomBase(BaseModel):
    italian_idiom: str
    rus_idiom: str

class IdiomRead(IdiomBase):
    italian_idiom: str
    rus_idiom: str


