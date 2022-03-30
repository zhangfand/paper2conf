from dataclasses import dataclass


@dataclass
class Doc:
    title: str
    content: str


@dataclass
class CloudDoc:
    path: str
    title: str