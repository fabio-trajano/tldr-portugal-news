import pytest
import scraper

def test_scrape_returns_list():
    ids = scraper.scrape()
    assert isinstance(ids, list)
