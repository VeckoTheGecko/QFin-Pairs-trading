def prefix_sum_init(prices):
	prefix_sum = [0 for i in prices]
	prefix_sum[0] = prices[0]
	for i in range(1, len(prices)):
		prefix_sum[i] = prefix_sum[i - 1] + prices[i]

	return prefix_sum

def calc_prefix_sum(prices, prefix_sum, start_index, end_index):
	for i in range(start_index + 1, end_index):
		prefix_array[i] = prefix_array[i - 1] + prices[i]

	return prefix_array

def prefix_sum_append(new_price, prefix_sum):
	prefix_sum.append(prefix_sum[-1] + new_price)

def prices_append(new_price, prices, prefix_sum):
	prices.append(new_price)
	prefix_sum_append(new_price, prefix_sum)

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

print("Test cases:")

prices = [1,2,3,4,5,6,7,8]
prefsum = prefix_sum_init(prices)
print(prefsum)
print(prices)
print()

prices_append(9, prices, prefsum)
moving_average(prefsum, 5, 5)

print()
print(prefsum)
print(prices)
print()

prices_append(10, prices, prefsum)
moving_average(prefsum, 5, 5)
moving_average(prefsum, 6, 5)

print()
print(prefsum)
print(prices)
print()

prices_append(10, prices, prefsum)
moving_average(prefsum, 6, 5)

print()
print(prefsum)
print(prices)
print()