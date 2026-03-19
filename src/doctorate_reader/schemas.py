from typing import List, Optional


class Paper:
    """Modelo sencillo para representar un paper académico.

    No usamos de momento Pydantic para mantener pocas dependencias en este
    paquete. Si más adelante exponemos una API o añadimos validación más
    estricta, se puede migrar fácilmente a BaseModel.
    """

    def __init__(
        self,
        title: str,
        authors: List[str],
        year: Optional[int] = None,
        abstract: Optional[str] = None,
        journal: Optional[str] = None,
        citations: Optional[int] = None,
        doi: Optional[str] = None,
        open_access: Optional[bool] = None,
        link: Optional[str] = None,
    ) -> None:
        self.title = title
        self.authors = authors
        self.year = year
        self.abstract = abstract
        self.journal = journal
        self.citations = citations
        self.doi = doi
        self.open_access = open_access
        self.link = link


__all__ = ["Paper"]


