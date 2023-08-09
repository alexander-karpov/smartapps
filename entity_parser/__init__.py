from entity_parser.parser import entity_parser


def parse_entity(text: str) -> list[dict]:
    response = []

    for m in entity_parser.findall(text):
        nomn = m.fact.inflect({ 'nomn' })
        accs = m.fact.inflect({ 'accs' })
        subject = nomn.subject()

        response.append({
            'nomn': str(nomn),
            'accs': str(accs),
            'subject': subject.name,
            'tags': str(subject.tag)
        })

    return response
