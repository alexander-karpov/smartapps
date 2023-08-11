from dataclasses import dataclass
from entity_parser.parser import entity_parser


@dataclass
class Entity:
    nomn: str
    accs: str
    subject: list[str]
    tags: str


def parse_entities(text: str) -> list[Entity]:
    response: list[Entity] = []

    for m in entity_parser.findall(text):
        nomn = m.fact.inflect({"nomn"})
        accs = m.fact.inflect({"accs"})
        subject = nomn.subject()

        response.append(Entity(str(nomn), str(accs), subject.name, str(subject.tag)))

    return response
