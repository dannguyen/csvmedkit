#!/usr/bin/env python3
import pandas as pd
from pathlib import Path


def main():
    path = Path('examples/drafts/fed-judges-service.csv')
    pd.read_csv(path)

if __name__ == '__main__':
    main()
