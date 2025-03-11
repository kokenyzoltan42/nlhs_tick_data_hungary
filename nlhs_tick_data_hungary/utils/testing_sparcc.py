import numpy as np
import pandas as pd

from nlhs_tick_data_hungary import data_path
from nlhs_tick_data_hungary.network.network_preparation.sparcc.sparcc_runner import SparCCRunner


def main():
    with open(data_path + f'/fake_data.txt', 'r+') as file:
        fake_data = pd.read_table(file)

    args = {
        'n_iter': 20,
        'x_iter': 70,
        'threshold': 0.1
    }
    # print(fake_data[1:].head())

    runner = SparCCRunner(df=fake_data.T,
                          args=args)
    result = runner.run()

    print(pd.DataFrame(result))

if __name__ == '__main__':
    main()
