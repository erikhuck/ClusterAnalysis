"""Finds the best clusterings for a cohort and data set and reports their number of clusters and clustering method"""

from os.path import join
from os import listdir, walk

from handler.utils import DATA_DIR, CSV_EXTENSION


def best_clustering_handler(cohort: str, dataset: str):
    """Main method of this module"""

    cur_dir: str = join(DATA_DIR, cohort, dataset)
    clustering_scores: dict = {}
    get_clustering_scores(cur_dir=cur_dir, clustering_scores=clustering_scores)
    max_score: float = max(clustering_scores.values())
    print('BEST SCORE:', max_score)
    print('PATHS TO CLUSTERINGS WITH BEST SCORE:')

    for path, score in clustering_scores.items():
        if score == max_score:
            print(path)


def get_clustering_scores(cur_dir: str, clustering_scores: dict):
    """Recursively creates a mapping from clustering CSV paths to clustering scores"""

    clustering_part: str = 'clustering-'
    sub_dirs: list = sorted(next(walk(cur_dir))[1])

    if len(sub_dirs) > 0:
        for sub_dir in sub_dirs:
            sub_dir: str = join(cur_dir, sub_dir)
            get_clustering_scores(cur_dir=sub_dir, clustering_scores=clustering_scores)
    else:
        paths: list = listdir(cur_dir)
        path = None
        score = None

        for path in paths:
            if clustering_part in path:
                path_parts: list = path.split('-')
                score: str = path_parts[-1][:-len(CSV_EXTENSION)]
                score: float = float(score)
                break

        assert path is not None and score is not None
        path: str = join(cur_dir, path)
        clustering_scores[path] = score
