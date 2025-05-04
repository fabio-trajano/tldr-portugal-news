import pytest
import clusterer

def test_cluster_empty():
    clusters = clusterer.cluster_by_date('1900-01-01')
    assert clusters == {}
