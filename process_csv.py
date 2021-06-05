import csv
import os

def read_file(filename):
	"""
	Return the head and the data (head, data)
	Takes a string to the file path/name as an input
	"""
	head = []
	data = []
	
	with open(filename) as industry_data:
		reader = csv.reader(industry_data)
		data_tuples = list(reader)
		head = data_tuples.pop(0)
		data = data_tuples

	return head, data


def group_companies_by_sector(filename):
	"""
	Return a map from sectors to symbols and a map from symbols to companies
	Takes a string to the file path/name as an input
	"""
	header, datatable 	= read_file(filename)
	sector_symbols_map 	= {}
	symbol_company_map 	= {}

	# makeshift way to filter out the data that isn't in the our dataset
	symbols = set()
	[symbols.add(file.split(".")[0]) for file in os.listdir("S&P500_3monthdata/ticker_breakdown")]

	for symbol, company, sector in datatable:
		if symbol not in symbols:
			continue

		sector_symbols = sector_symbols_map.get(sector, [])
		sector_symbols.append(symbol)
		sector_symbols_map[sector] = sector_symbols

		symbol_company_map[symbol] = company

	return sector_symbols_map, symbol_company_map


def get_company_names(symbols_list, symbols_map):
	"""
	Returns a list of companies given a list of symbols and a way to map them
	"""
	return [symbols_map[symbol] for symbol in symbols_list]