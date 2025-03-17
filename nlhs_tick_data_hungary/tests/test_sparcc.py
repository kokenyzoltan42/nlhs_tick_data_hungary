import json

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from nlhs_tick_data_hungary import config_path
from nlhs_tick_data_hungary.data.utils.google_data_downloader import GoogleDataDownloader
from nlhs_tick_data_hungary.network.network_preparation.sparcc.sparcc_runner import SparCCRunner


def main():
    with open(config_path + f'/links.json', 'r+') as file:
        links = json.load(file)

    fake_data_dl = GoogleDataDownloader(
        file_url=links['fake_data_for_sparcc'],
        file_name='fake_data.txt'
    )

    true_basis_cor_dl = GoogleDataDownloader(
        file_url=links['true_basis_cor_for_sparcc'],
        file_name='true_basis_cor.txt'
    )

    fake_data = pd.read_table(fake_data_dl.file_path, sep='\t')
    true_basis_cor = pd.read_table(true_basis_cor_dl.file_path, sep='\t')

    args = {
        'n_iter': 20,
        'x_iter': 70,
        'threshold': 0.1
    }

    runner = SparCCRunner(data=fake_data.T,  # Próbáltam megoldani hogy transzponálás nélkül is működjön, de
                          # nem akar összejönni
                          args=args)
    result = runner.run()

    print(pd.DataFrame(result))

    # Rájöttem, hogy ezek a metrikák sokat nem érnek, mert sok 0-hoz közeli érték van és azokanál nem igazán számít
    # a különbség
    mae = mean_absolute_error(true_basis_cor.iloc[:, 1:], result)
    print(f"\n\nMean Absolute Error: {mae}")

    mse = mean_squared_error(true_basis_cor.iloc[:, 1:], result)
    print(f"\nMean Squared Error: {mse}")


if __name__ == '__main__':
    main()