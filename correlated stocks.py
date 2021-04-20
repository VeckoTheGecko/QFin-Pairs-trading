import numpy as np
import os
import pandas as pd


def open_files(name):
    data = np.zeros(shape=(1260, 1))
    df = pd.DataFrame(data)
    for filename in os.listdir(name):
        directory = os.join(name + filename)
        col = pd.read_csv(directory, usecols=["open"])
        df[filename] = col
    df.drop(df.columns[[0]], axis=1, inplace=True)
    return df


def get_corrs(df):
    corrs = df.corr()
    for i in range(505):
        corrs.iat[i, i] = 0.0
    corrs = corrs.unstack()
    corrs = corrs.sort_values(ascending=False)
    print(corrs)


def main():
    get_corrs(open_files("individual_stocks_5yr"))


if __name__ == '__main__':
    main()
