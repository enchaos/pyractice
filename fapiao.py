import sys
from itertools import combinations


def get_mix_sum(total, seperates):
	posibilities = []
	for i in range(2, len(seperates)+1):
		posibilities += list(combinations(seperates, i))
	
	summaries = [(sum(p), p) for p in posibilities if sum(p) > total]
	
	result = sorted(summaries, key=lambda summary: summary[0])
	return result


if(__name__=='__main__'):
	if len(sys.argv)!=3:
		exit('Please run it in "fapiao.py <total> <amount 1>,<amount 2>,...,<amount n>" format...')
	else:
		try:
			total = float(sys.argv[1])
			seperates = [float(i) for i in sys.argv[2].split(',')]
			result = get_mix_sum(total, seperates)
			print('-'*50)
			print("The best choices of fapiao are: %s." % str(result[0][1]))
			print("\nAll options are:\n\n(summary, (combinations))\n")
			for i in result: print(i)
			print('-'*50)
		except Exception as e:
			exit(e)
