import numpy as np


class CLRCalculator:
    def __init__(self, data: np.ndarray):
        self.data = data

    def run(self):
        pass

    def clr(self) -> np.ndarray:
        frame_temp = np.log(self.data)

        mean = np.mean(frame_temp,
                       axis=1,  # vagy 0?
                       keepdims=True)
        clr = frame_temp - mean

        return clr

    def run_clr(self):
        z = self.clr()
        correlations = np.corrcoef(z,
                                   rowvar=False)  # vagy True?

        return correlations
