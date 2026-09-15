from runner import execute

r = execute()
for pair, data in r['pairwise'].items():
    verdict = 'EQUIVALENT' if data['exact_state_match'] else 'DIVERGENT'
    print(f'{pair}: {verdict}; max_state_euclidean_divergence={data["max_state_euclidean_divergence"]}')
