# content of test_sample.py
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5

def test_other():
    assert func(3) == 4
