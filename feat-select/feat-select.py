from sys import stdin
from sys import argv

rank_output: str = stdin.read()

rank_output: list = rank_output.split('\n')
cut_idx: int = rank_output.index('Ranked attributes:') + 1
rank_output: list = rank_output[cut_idx:]

while '' in rank_output:
    rank_output.remove('')

feats_to_keep: list = []
for item in rank_output:
    if 'Selected attributes:' in item:
        break

    feat: str = item.split(' ')[-1]
    feats_to_keep.append(feat)

threshold: str = argv[1]
print('Keeping {} features using a threshold of {}'.format(len(feats_to_keep), threshold))

output_file_name: str = 'feat-select/kept-feats-{}.txt'.format(threshold)
with open(output_file_name, 'w') as f:
    for feat in feats_to_keep:
        f.write(feat + '\n')

