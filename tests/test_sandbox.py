import pytest

from factory.sandbox import CandidateRejected, check_source


@pytest.mark.parametrize("src", [
    "import os",
    "import subprocess",
    "from pathlib import Path",
    "import requests",
    "x = open('f')",
    "x = eval('1')",
    "import pandas as pd\npd.read_csv('x')",
    "x = ().__class__",
])
def test_rejects_unsafe(src):
    with pytest.raises(CandidateRejected):
        check_source(src)


def test_allows_normal_strategy():
    check_source("import numpy as np\nimport pandas as pd\nfrom strategies.base import Strategy\n")
