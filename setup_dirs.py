from stock_data import Stock

"""
Use this to bakc up and then remove all the figures: can't guarantee it will work though

cp -r comparison_tests backups/n (write in a number instead of n)
rm comparison_tests/*/*.png

these should probably be shell scripts honeslty
"""

if __name__ == "__main__":
	os.system("mkdir comparison_tests")
	stocks_by_industry = Stock.all_by_industry()
	for industry in stocks_by_industry.keys():
		iname = industry.replace(" ", "\\ ")
		os.system(f"cd comparison_tests; mkdir {iname}")
		os.system(f"cd comparison_tests; cd {iname}; echo \"# Analysis of the {industry} Sector\" > readme.md")