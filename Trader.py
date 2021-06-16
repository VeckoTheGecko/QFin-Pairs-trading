class Trader:
	def __init__(self, stock1, stock2):
		# df1 = pd.read_csv(stock1.file_path)
		# df2 = pd.read_csv(stock2.file_path)

		# prices1 = df1[df1.columns[1]]
		# prices2 = df2[df2.columns[1]]

		self.shrt_on_spread = False
		self.long_on_spread = False

	def tick(self):
		mavg_30 = np.mean(self.stock_prices[0] - self.stock_prices[1])
		std_30 = np.std(self.stock_prices[0] - self.stock_prices[1])
		mavg_1 = np.mean(short_self.stock_prices[0] - short_self.stock_prices[1])

		if std_30 > 0:
			zscore = (mavg_1 - mavg_30) / std_30
			
			# Spread = CNQ - PXD
			if zscore > 1.2 and not self.shrt_on_spread:
				order_target_percent(cnq, -0.5) 
				order_target_percent(pxd, 0.5) 
				context.shorting_spread = True
				context.long_on_spread = False
				
			elif zscore < 1.2 and not self.long_on_spread:
				order_target_percent(cnq, 0.5) 
				order_target_percent(pxd, -0.5) 
				context.shorting_spread = False
				context.long_on_spread = True
				
			elif abs(zscore) < 0.1:
				order_target_percent(cnq, 0)
				order_target_percent(pxd, 0)
				context.shorting_spread = False
				context.long_on_spread = False
					
			record(Z_score = zscore)

	def __repr__(self):
		return f's1: {self.stock_prices[0][:5]}, s2: {self.stock_prices[1][:5]}'
