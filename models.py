
from typing import List, Dict, Union , Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()



class GetStableCoinsInput(BaseModel):
    top_m: Optional[int] = 5

class InternetSearchInput(BaseModel):
    query: str
    region: Optional[str] = "wt-wt"
    max_results: Optional[int] = 5

class InternetSearchOutput(BaseModel):
    results: List[Dict]

class GetPoolsInput(BaseModel):
    top_n: Optional[int] = 5

class GetPoolsOutput(BaseModel):
    pools: List[Dict[str, Union[str, int, float]]]

class GetStableCoinsInput(BaseModel):
    top_m: Optional[int] = 5


class GetStableCoinsPriceInput(BaseModel):
    dummy : bool = True