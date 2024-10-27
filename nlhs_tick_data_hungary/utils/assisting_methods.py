import numpy as np


class AssistingMethods:
    @staticmethod
    def create_crosstable(df):
        # out = pd.get_dummies(data=df.iloc[:, 1:].stack()).sum().ne(0).astype(int)
        final = df.dot(df.T).astype(float)
        np.fill_diagonal(final.values, np.nan)
        return final
