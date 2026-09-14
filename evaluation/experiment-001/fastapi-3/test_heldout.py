"""Evaluator-only behavioral checks for FastAPI 3."""

from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field
from starlette.testclient import TestClient


class Entry(BaseModel):
    label: str = Field(..., alias="display_label")
    count: int = None


app = FastAPI()


@app.get("/nested-list", response_model=List[List[Entry]], response_model_exclude_unset=True)
def nested_list():
    return [[Entry(display_label="first"), Entry(display_label="second", count=2)]]


@app.get("/nested-map", response_model=Dict[str, List[Entry]], response_model_exclude_unset=True)
def nested_map():
    return {"group": [Entry(display_label="third"), Entry(display_label="fourth", count=4)]}


def test_nested_list_response_models_preserve_aliases_and_unset_fields():
    client = TestClient(app)

    list_response = client.get("/nested-list")
    list_response.raise_for_status()
    assert list_response.json() == [[
        {"display_label": "first"},
        {"display_label": "second", "count": 2},
    ]]


def test_nested_map_response_models_preserve_aliases_and_unset_fields():
    client = TestClient(app)

    map_response = client.get("/nested-map")
    map_response.raise_for_status()
    assert map_response.json() == {"group": [
        {"display_label": "third"},
        {"display_label": "fourth", "count": 4},
    ]}
