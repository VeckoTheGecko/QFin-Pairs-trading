#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os

from correlated_stocks import *
from process_csv import *

symbols_by_sector, company_by_symbol = group_companies_by_sector("constituents_csv.csv")
tech_companies = symbols_by_sector["Information Technology"]

print(tech_companies)
print()

tech_companies = [company_by_symbol[x] for x in tech_companies]

print(tech_companies)

a = np.zeros(50)
plt.plot(a)
plt.savefig(os.path.join("figures", "fig.png"))