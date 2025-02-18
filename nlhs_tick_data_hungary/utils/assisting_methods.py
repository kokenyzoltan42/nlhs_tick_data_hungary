import numpy as np


class AssistingMethods:
    # TODO: type annotations
    @staticmethod
    def create_crosstable(df):
        # out = pd.get_dummies(data=df.iloc[:, 1:].stack()).sum().ne(0).astype(int)
        final = df.dot(df.T).astype(float)
        np.fill_diagonal(final.values, np.nan)
        return final

    @staticmethod
    def select_type(df, to_type):
        if to_type == 'Hímek':
            df = df.filter(like='Male')
        elif to_type == 'Nőstények':
            df = df.filter(like='Female')
        elif to_type == 'Összes':
            pass

        return df
