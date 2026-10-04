import pandas as pd

from factory import news


IDX = pd.DatetimeIndex(pd.to_datetime(["2024-03-07", "2024-03-08", "2024-03-11"]))  # Thu, Fri, Mon


def arts(*rows):
    return pd.DataFrame([(i, t, s, "") for i, (t, s) in enumerate(rows)], columns=news.COLUMNS)


def test_article_after_close_rolls_to_next_bar():
    # 15:59 ET (20:59Z in EST) counts today; 16:01 ET counts on the next bar
    a = arts(("2024-03-07T20:59:00Z", "AAPL"), ("2024-03-07T21:01:00Z", "AAPL"))
    p = news.count_panel(a, IDX, ["AAPL"])
    assert p["AAPL"].tolist() == [1.0, 1.0, 0.0]


def test_weekend_news_lands_on_monday_and_multi_symbol_counts_each():
    a = arts(("2024-03-09T15:00:00Z", "AAPL|MSFT"), ("2024-03-12T15:00:00Z", "AAPL"))  # Sat; after last bar
    p = news.count_panel(a, IDX, ["AAPL", "MSFT"])
    assert p.loc["2024-03-11"].tolist() == [1.0, 1.0]
    assert p.to_numpy().sum() == 2.0


def test_truncated_index_gives_identical_rows():
    a = arts(("2024-03-07T14:00:00Z", "AAPL"), ("2024-03-08T23:00:00Z", "AAPL"))
    full = news.count_panel(a, IDX, ["AAPL"])
    short = news.count_panel(a, IDX[:2], ["AAPL"])
    pd.testing.assert_frame_equal(full.iloc[:2], short)


def test_headline_score_and_sentiment_panel():
    assert news.headline_score("Apple Beats Estimates, Raises Guidance") == 2.0
    assert news.headline_score("Analyst downgrades MSFT after earnings miss") == -2.0
    assert news.headline_score("Microsoft to host developer conference") == 0.0
    a = pd.DataFrame([(1, "2024-03-07T14:00:00Z", "AAPL", "Apple beats estimates"),
                      (2, "2024-03-07T21:30:00Z", "AAPL", "Apple faces antitrust probe")], columns=news.COLUMNS)
    p = news.sentiment_panel(a, IDX, ["AAPL"])
    assert p["AAPL"].tolist() == [1.0, -2.0, 0.0]
