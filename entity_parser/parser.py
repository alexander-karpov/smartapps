from dataclasses import dataclass
from typing import List
from yargy import ( Parser, rule, or_, and_, not_ )
from yargy.predicates import ( gram, eq, normalized, dictionary )
from yargy.interpretation import ( fact, attribute )
from yargy.relations import main, number_relation, case_relation
from entity_parser.yargy_fix import not_grams
from entity_parser.morph import inflect, get_tag

'''
Для согласований нужна согласованность по числу и падежу,
но не по роду
'''
class nc_relation(number_relation, case_relation):
    label = 'nc'

    def __call__(self, form, other):
        return (
            number_relation.__call__(self, form, other)
            and case_relation.__call__(self, form, other)
        )


@dataclass(repr=True)
class Subject:
    name: List[str]
    tag: str


class Agreement(fact(
    'Agreement',
    [attribute("adjf").repeatable(), attribute("noun").repeatable(), 'tag']
)):
    def __str__(self):
        return " ".join(self.adjf + self.noun)

    def subject(self) -> Subject:
        return Subject(self.noun, self.tag)

    def inflect(self, grs):
        noun_tags = get_tag(self.noun[0])
        adjf_tags = get_tag(self.adjf[0]) if self.adjf else None

        new_tags = { noun_tags.number }

        if 'nomn' not in grs and 'masc' in noun_tags:
            new_tags.add(noun_tags.animacy)

        # Чёрного в+орона распознаётся как Чёрная вор+она
        # Это неправильно. Если у adjf есть gender, можно использовать его
        if 'sing' in noun_tags and adjf_tags and adjf_tags.gender:
            new_tags.add(adjf_tags.gender)
        elif 'sing' in noun_tags and noun_tags.gender:
            new_tags.add(noun_tags.gender)

        new_tags.discard(None)

        inflected_nouns  = [inflect(n, [grs | new_tags, grs]) for n in self.noun]

        return Agreement(
            adjf=[inflect(a, [grs | new_tags, grs])[0] for a in self.adjf],
            noun=[noun for noun, tag in inflected_nouns],
            tag=inflected_nouns[0][1]
        )


class GovermentPart(fact(
    'GovermentPart',
    [attribute('noun').repeatable(), 'agreement', 'tag']
)):
    def __str__(self):
        if self.agreement:
            return str(self.agreement)

        return " ".join(self.noun)

    def subject(self) -> Subject:
        if self.agreement:
            return self.agreement.subject()

        return Subject(self.noun, self.tag)

    def inflect(self, grs):
        if self.agreement:
            return GovermentPart(
                agreement=self.agreement.inflect(grs)
            )

        inflected = [inflect(n, [grs]) for n in self.noun]

        return GovermentPart(
            noun=[noun for noun, tag in inflected],
            tag=inflected[0][1]
        )


class Goverment(fact(
    'Goverment',
    ['main', 'dependend', 'prep']
)):
    def __str__(self):
        if self.prep:
            return f"{self.main} {self.prep} {self.dependend}"

        return f"{self.main} {self.dependend}"

    def subject(self) -> Subject:
        return self.main.subject()

    def inflect(self, grs):
        return Goverment(
            main=self.main.inflect(grs),
            prep=self.prep,
            dependend=self.dependend,
        )


class Collocation(fact(
    'Collocation',
    ['noun', 'agreement', 'goverment', 'tag']
)):
    def __str__(self) -> str:
        if self.noun:
            return self.noun

        if self.agreement:
            return str(self.agreement)

        if self.goverment:
            return str(self.goverment)

        assert False, "Хотя бы один вариант должен быть"

    def subject(self) -> Subject:
        if self.noun:
            return Subject([self.noun], self.tag)

        if self.agreement:
            return self.agreement.subject()

        if self.goverment:
            return self.goverment.subject()

    def inflect(self, grs):
        if self.noun:
            noun, tag = inflect(self.noun, [grs])
            return Collocation(noun=noun, tag=tag)

        if self.agreement:
            return Collocation(agreement=self.agreement.inflect(grs))

        if self.goverment:
            return Collocation(goverment=self.goverment.inflect(grs))

        return self


def make_noun(*and_this):
    return or_(
        and_(
            gram("NOUN"),
            not_(gram("PREP")), # Предлоги
            not_(gram("PRCL")), # Частицы
            not_(gram("ADVB")), # Наречия
            not_(normalized('быть')),
            *and_this,
        ),
        # больной проказой
        and_(
            gram("ADJF"),
            gram("Subx"),
            not_(gram("Apro")), # Местоимение
            *and_this,
        ),
        # радиоведущий
        # телевизионный ведущий
        # заключённый, прокаженный
        and_(
            gram("PRTF"),
            gram("Subx"),
            *and_this,
        ),
        eq('хрен'), # Является частицей
        eq('уж'), # Является частицей
        normalized('ток'), # Является частицей, видимо
        normalized('тип'), # Является частицей, видимо
    )


def make_adjf(*and_this):
    return or_(
        and_(
            gram("ADJF"),
            not_(gram("Apro")), # такой
            not_(dictionary({'съедобное', 'полезные', 'вкусное'})),
            # Захватывает Допустим как Допустимый
            not_(gram("VERB")),
            *and_this,
        ),
        # орбитальная:ADJF пилотируемая:PRTF станция
        and_(
            gram("PRTF"),
            *and_this,
        )
    )


NOUN = make_noun()
NOUN_not_nomn = make_noun(not_grams({'nomn', 'sing'}))
ADJF = make_adjf()
PREP = gram("PREP")


def make_agreement(*, noun = NOUN):
    nc_rel = nc_relation()

    return or_(
        # белая курица
        rule(
            ADJF.match(nc_rel).optional().interpretation(
                Agreement.adjf
            ),
             ADJF.match(nc_rel).interpretation(
                Agreement.adjf
            ),
             main(noun.match(nc_rel).interpretation(
                Agreement.noun
            )),
        ),
        # рябина красная
        rule(
            main(noun.match(nc_rel).interpretation(
                Agreement.noun
            )),
            ADJF.match(nc_rel).interpretation(
                Agreement.adjf
            ),
        ),
        # застежка липучка
        rule(
            main(noun.match(nc_rel).interpretation(
                Agreement.noun
            )),
            noun.match(nc_rel).interpretation(
                Agreement.noun
            ),
        ),
    ).interpretation(
        Agreement
    )


GOVERMENT_MAIN = or_(
    rule(NOUN).interpretation(
        GovermentPart.noun
    ),
    make_agreement().interpretation(
        GovermentPart.agreement
    ),
).named("GOVERMENT_MAIN").interpretation(
    GovermentPart
)


GOVERMENT_DEPENDEND = or_(
    rule(NOUN_not_nomn).interpretation(
        GovermentPart.noun
    ),
    make_agreement(noun=NOUN_not_nomn).interpretation(
        GovermentPart.agreement
    ),
    # борец за хорошего человека
    #          -----------------
    rule(NOUN_not_nomn, NOUN_not_nomn).interpretation(
        GovermentPart.noun
    ),
).named("GOVERMENT_DEPENDEND").interpretation(
    GovermentPart
)


GOVERMENT = rule(
    GOVERMENT_MAIN.interpretation(
        Goverment.main
    ),
    PREP.optional().interpretation(
        Goverment.prep
    ),
    GOVERMENT_DEPENDEND.interpretation(
        Goverment.dependend
    ),
).named("GOVERMENT").interpretation(
    Goverment
)


COLLOCATION = or_(
    rule(NOUN).interpretation(
        Collocation.noun
    ),
    make_agreement().interpretation(
        Collocation.agreement
    ),
    GOVERMENT.interpretation(
        Collocation.goverment
    ),
).named("COLLOCATION").interpretation(
    Collocation
)


entity_parser = Parser(COLLOCATION)
