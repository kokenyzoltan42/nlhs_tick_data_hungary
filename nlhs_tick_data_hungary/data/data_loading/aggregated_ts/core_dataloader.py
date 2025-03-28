from abc import ABC, abstractmethod
import json
import typing

from nlhs_tick_data_hungary import config_path


class CoreDataLoader(ABC):
    """
    A base class for all the data loaders that handle aggregated timeseries data.

    result (dict): A dictionary that stores the processed data.
    links (dict): A dictionary containing the URLs for the data files.
    """

    def __init__(self, use_cache: bool = False):
        """
        Initializes the core data loader by loading the config links.
        The `run` method is not called automatically, subclasses call it when needed.

        :param bool use_cache: Whether to load the data from the cached files.
        """
        self.use_cache = use_cache
        self.result = None
        self.links = self.load_links()

    @staticmethod
    def load_links() -> typing.Dict[str, str]:
        """
        Loads the links for the data files from the `links.json` config file.

        :return dict: A dictionary containing the URLs for data files.
        """
        with open(config_path + f'/links.json', 'r+') as file:
            return json.load(file)

    @abstractmethod
    def run(self) -> None:
        """
        Abstract method to be implemented in subclasses for running the data loading and processing pipeline.
        """
        pass

    @abstractmethod
    def preprocess_data(self, *args, **kwargs):
        """
        Abstract method for data preprocessing, to be implemented in subclasses.
        """
        pass
