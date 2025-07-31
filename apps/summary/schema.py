from ninja import Schema
from typing import Optional, List
from datetime import datetime

class AISummary(Schema):
    message: str
    date: str