from urllib import parse
from yargy import ( Parser, rule, or_, and_, not_ )
from yargy.predicates import ( gram, eq, normalized, dictionary )
from yargy.interpretation import ( fact, attribute )
from yargy.relations import gnc_relation, main
from dialog import Intent
from yargy_fix import not_grams
from morph import inflect, get_tag


class Agreement(fact(
    'Agreement',
    [attribute("adjf").repeatable(), attribute("noun").repeatable()]
)):
    def __str__(self):
        return " ".join(self.adjf + self.noun)

    def inflect(self, grs):
        noun_tags = get_tag(self.noun[0])

        adjf_tags = { noun_tags.number }

        if 'nomn' not in grs and 'masc' in noun_tags:
            adjf_tags.add(noun_tags.animacy)

        if 'sing' in noun_tags:
            adjf_tags.add(noun_tags.gender)

        # if noun_parsed.tag.number == 'sing' and not (
        #     noun_parsed.tag.gender == 'neut' and noun_parsed.tag.animacy == 'inan'
        # ):
        #     adjf_tags.add(noun_parsed.tag.gender)

        # if noun_parsed.tag.animacy == 'inan' and 'nomn' not in grs:
        #     adjf_tags.add('inan')

        return Agreement(
            adjf=[inflect(a, grs | adjf_tags) for a in self.adjf],
            noun=[inflect(n, grs) for n in self.noun],
        )


class GovermentPart(fact(
    'GovermentPart',
    [attribute('noun').repeatable(), 'agreement']
)):
    def __str__(self):
        if self.agreement:
            return str(self.agreement)

        return " ".join(self.noun)

    def inflect(self, grs):
        if self.agreement:
            return GovermentPart(
                agreement=self.agreement.inflect(grs)
            )

        return GovermentPart(
            noun=[inflect(n, grs) for n in self.noun]
        )


class Goverment(fact(
    'Goverment',
    ['main', 'dependend', 'prep']
)):
    def __str__(self):
        if self.prep:
            return f"{self.main} {self.prep} {self.dependend}"

        return f"{self.main} {self.dependend}"

    def inflect(self, grs):
        return Goverment(
            main=self.main.inflect(grs),
            prep=self.prep,
            dependend=self.dependend,
        )


class Collocation(fact(
    'Collocation',
    ['noun', 'agreement', 'goverment']
)):
    def __str__(self) -> str:
        if self.noun:
            return self.noun

        if self.agreement:
            return str(self.agreement)

        if self.goverment:
            return str(self.goverment)

        assert False, "Хотя бы один вариант должен быть"

    def inflect(self, grs):
        if self.noun:
            return Collocation(noun=inflect(self.noun, grs))

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
            not_(eq('алиса')),
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
    gnc = gnc_relation()

    return or_(
        # белая курица
        rule(
            ADJF.match(gnc).optional().interpretation(
                Agreement.adjf
            ),
             ADJF.match(gnc).interpretation(
                Agreement.adjf
            ),
             main(noun.match(gnc).interpretation(
                Agreement.noun
            )),
        ),
        # рябина красная
        rule(
            main(noun.match(gnc).interpretation(
                Agreement.noun
            )),
            ADJF.match(gnc).interpretation(
                Agreement.adjf
            ),
        ),
        # застежка липучка
        rule(
            main(noun.match(gnc).interpretation(
                Agreement.noun
            )),
            noun.match(gnc).interpretation(
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


class EntityIntent(Intent):
    collocation: Collocation

    def match(self, command: str) -> bool:
        match = entity_parser.find(command)

        if not match:
            return False

        self.collocation = match.fact

        return True
