from stock_data import Stock

if __name__ == "__main__":
	os.system("mkdir comparison_tests")
	stocks_by_industry = Stock.all_by_industry()
	for industry in stocks_by_industry.keys():
		iname = industry.replace(" ", "\\ ")
		os.system(f"cd comparison_tests; mkdir {iname}")
		os.system(f"cd comparison_tests; cd {iname}; echo \"# Analysis of the {industry} Sector\" > readme.md")