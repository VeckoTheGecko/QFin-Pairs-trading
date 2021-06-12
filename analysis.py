import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from stock_data import Stock

import sys

if __name__ == "__main__":
	Stock.analyze_industries(industries_to_analyze=sys.argv[1:])#Stock.all_industries())
	# AMD = Stock("AMD")
	# print(AMD)
	# print(AMD.pricedata)
	# print(AMD.pricedata.loc[:,'price'])
	# print(AMD.pricedata[:,"price"])