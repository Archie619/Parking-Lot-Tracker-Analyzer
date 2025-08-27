# just an example of a function in a router, will be deleted later...

from fastapi import APIRouter

router = APIRouter()

'''
Example docstring (desc of function)
'''
def example(ex1: int, ex2: str):
    return ex1 + ex2