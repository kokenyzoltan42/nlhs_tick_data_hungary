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
        'threshold': 0.2
    }
    # print(fake_data[1:].head())

    runner = SparCCRunner(df=fake_data.T,# / fake_data[1:].sum(axis=0),
                          args=args)
    result = runner.run()

    print(pd.DataFrame(result))
    print(result[result < (0.99)].max().max())
    print(np.unravel_index(np.argmax(result[result < 0.99]), result.shape))
    print(result[np.unravel_index(np.argmax(result[result < 0.99]), result.shape)])


if __name__ == '__main__':
    main()
