# prefix sum = cummulative sum
# simple moving average calculated using the 'boxcar filter'

# gets an array of the prefix sum given an array of prices
def prefix_sum_init(prices):
	prefix_sum = [0 for i in prices]
	prefix_sum[0] = prices[0]
	for i in range(1, len(prices)):
		prefix_sum[i] = prefix_sum[i - 1] + prices[i]

	return prefix_sum

# calcuulates the prefix sum between two indices
def calc_prefix_sum(prices, prefix_sum, start_index, end_index):
	for i in range(start_index + 1, end_index):
		prefix_array[i] = prefix_array[i - 1] + prices[i]

	return prefix_array

# appends a new element to the prefix sum given a new price
def prefix_sum_append(new_price, prefix_sum):
	prefix_sum.append(prefix_sum[-1] + new_price)

# appends a new element to the price and updates the prefix sum accordingly
def prices_append(new_price, prices, prefix_sum):
	prices.append(new_price)
	prefix_sum_append(new_price, prefix_sum)

# gets the moving average of the n items after a start time
def moving_average(prefix_sum, num_timesteps, start_timestep):
	if len(prefix_sum) - num_timesteps < start_timestep:
		print("Can't calculate moving average: too few number of terms")
		return -1

	start_timestep -= 1
	end_timestep = num_timesteps + start_timestep

	range_sum = prefix_sum[end_timestep] - prefix_sum[start_timestep]
	range_mean = range_sum / (num_timesteps)

	print(f"Sum from index {start_timestep:2.0f} to {end_timestep:2.0f} : {range_mean:.2f}")

	return range_mean

# gets the moving average of a given interval
def moving_average_by_bounds(prefix_sum, lower, upper):
	if lower < 0:
		print("lower bound out of bounds of the prefix array")
		return

	if upper >= len(prefix_sum):
		print("upper bound out of bounds of the prefix array")
		return

	# the prefix sum is equal to the price at index 0
	if lower != 0:
		lower_pref = prefix_sum[lower - 1]

	else:
		lower_pref = 0

	upper_pref = prefix_sum[upper]


	average = (upper_pref - lower_pref) / (upper - lower + 1)
	return average