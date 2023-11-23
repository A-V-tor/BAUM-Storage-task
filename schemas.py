from pydantic import BaseModel


class AvgCount(BaseModel):
    date: str
    title: str
    x_avg_count_in_line: float
