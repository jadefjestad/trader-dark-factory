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


@pytest.mark.parametrize("src", [
    "from pandas import read_pickle as reader",
    "import numpy as np\nnp.savetxt('x', [1])",
    "from numpy import *",
    "import pandas as pd\npd.DataFrame().query('a')",
    "x = (1).real._x",
])
def test_rejects_file_and_eval_entry_points(src):
    with pytest.raises(CandidateRejected):
        check_source(src)
