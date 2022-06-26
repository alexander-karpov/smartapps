class Intent:
    samples: tuple[str, ...]
    threshold: float

    def __init__(self, *samples: str, threshold = 0.9) -> None:
        self.samples = samples
        self.threshold = threshold
