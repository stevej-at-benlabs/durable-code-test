#!/usr/bin/env python3

from typing import Any


def calculate_total(items: list[float]) -> float:
    total = 0.0
    for item in items:
        total += item
    print(f"Total calculated: {total}")  # This should be caught
    return total


class DataProcessor:
    def process_data(self, data: Any) -> Any:
        print("Processing data...")  # This should be caught
        result = data * 2
        print(f"Result: {result}")  # This should be caught
        return result
