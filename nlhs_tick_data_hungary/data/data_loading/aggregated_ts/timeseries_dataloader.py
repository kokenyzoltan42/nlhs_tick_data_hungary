from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.lyme_dataloader import LymeDataLoader
from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.pilis_tick_dataloader import PilisTickDataLoader
from nlhs_tick_data_hungary.data.data_loading.aggregated_ts.rainfall_dataloader import RainfallDataLoader


class TimeseriesDataLoader:
    """
    A class to load and aggregate time-series data for Lyme disease, tick data from Pilis, and rainfall data.

    This class serves as a central data loader or timeseries related datas. The results are stored in a dictionary.

    data (dict): A dictionary holding the processed results of Lyme disease data, Pilis tick data, and rainfall data.


    Structure of the `data` attribute after the `run` method is called:
    `self.data` = {
        - 'lyme_data':
            - 'lyme_data_year': number of Lyme diseases in each year
            - 'lyme_data_month': number of Lyme diseases in each month
        - 'rainfall_data':
            - 'piiscsaba': rainfall data in Piliscsaba
            - 'pilisszentkereszt': rainfall data in Pilisszentkereszt
        'pilis_tick_data':
            - 'monthly_data': data of ticks found at Pilis aggregated monthly
            - 'regular_data': data of ticks found at Pilis without aggregation
    }
    """

    def __init__(self):
        """
        Initializes the TimeseriesDataLoader with an empty dictionary to store the results of the data loading process.
        """
        self.data = {}

    def run(self) -> None:
        """
        Runs the data loading process by initializing the data loaders for Lyme disease, Pilis tick data,
        and rainfall data. It stores the results in the `self.data` attribute,
        which holds a dictionary of the loaded data.

        The dictionary `self.data` will contain the following keys:
        - 'lyme_data': Loaded and processed Lyme disease data.
        - 'pilis_data': Loaded and processed tick data for Pilis.
        - 'rainfall_data': Loaded and processed rainfall data.
        """
        # Initialize the individual data loaders for Lyme disease, Pilis tick data, and rainfall data
        lyme_dataloader = LymeDataLoader()
        pilis_dataloader = PilisTickDataLoader()
        rainfall_dataloader = RainfallDataLoader()

        # Aggregate the results from each data loader and store them in the `self.data` dictionary
        self.data = {
            'lyme_data': lyme_dataloader.result,
            'pilis_data': pilis_dataloader.result,
            'rainfall_data': rainfall_dataloader.result
        }
