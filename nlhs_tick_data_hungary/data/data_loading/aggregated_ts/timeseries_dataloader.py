from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.lyme_dataloader import LymeDataLoader
from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.pilis_tick_dataloader import PilisTickDataLoader
from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.rainfall_dataloader import RainfallDataLoader


class TimeseriesDataLoader:
    def __init__(self):
        self.data = {}

    # TODO: change implementation diagram
    def run(self) -> None:
        lyme_dataloader = LymeDataLoader()
        pilis_dataloader = PilisTickDataLoader()
        rainfall_dataloader = RainfallDataLoader()

        self.data = {
            'lyme_data': lyme_dataloader.result,
            'pilis_data': pilis_dataloader.result,
            'rainfall_data': rainfall_dataloader.result
        }
