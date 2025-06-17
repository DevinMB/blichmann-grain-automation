class FakeButton:
    def __init__(self): self.is_pressed = False

class FakeLED:
    def __init__(self): self.is_lit = False
    def on(self):  self.is_lit = True
    def off(self): self.is_lit = False

class FakeHX:
    def __init__(self, weights):  # iterable of successive readings
        self._weights = list(weights)
    def get_weight(self, _):      # ignore times parameter
        return self._weights.pop(0) if self._weights else 0

class FakePixel(list):
    def __init__(self): super().__init__([(0,0,0)])
