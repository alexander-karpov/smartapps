from yargy.predicates import ( AndPredicate )
from yargy.predicates.constructors import ParameterPredicateScheme, ParameterPredicate
from yargy.predicates.bank import morph_required


def AndPredicate_constrain(self, token):
    if not hasattr(token, 'constrained'):
        return token

    forms = None

    for p in self.predicates:
        if p(token):
            constrained = p.constrain(token)

            if not hasattr(constrained, 'forms'):
                continue

            if not forms:
                forms = set(p.constrain(token).forms)
            else:
                forms &= set(p.constrain(token).forms)

    return token.constrained(list(forms))

AndPredicate.constrain = AndPredicate_constrain


class grams(ParameterPredicateScheme):
    def activate(self, context):
        for gr in self.value:
            context.tokenizer.morph.check_gram(gr)
        return GramsPredicate(self.value)


class GramsPredicate(ParameterPredicate):
    @morph_required
    def __call__(self, token):
        return any(
            all((v in _.grams for v in self.value))
            for _ in token.forms
        )

    def constrain(self, token):
        return token.constrained([
            _ for _ in token.forms
            if all((v in _.grams for v in self.value))
        ])

    @property
    def label(self):
        return "gram('%s')" % self.value


class not_grams(ParameterPredicateScheme):
    def activate(self, context):
        for gr in self.value:
            context.tokenizer.morph.check_gram(gr)
        return NotGramsPredicate(self.value)


class NotGramsPredicate(ParameterPredicate):
    @morph_required
    def __call__(self, token):
        return any(
            True
            for _ in token.forms
            if not all((v in _.grams for v in self.value))
        )

    def constrain(self, token):
        return token.constrained([
            _ for _ in token.forms
            if not all((v in _.grams for v in self.value))
        ])

    @property
    def label(self):
        return "gram('%s')" % self.value
