from app.services.calculation_service import build_calculation_result


def test_build_calculation_result_totals_items() -> None:
    payload = {
        'items': [
            {'name': 'A', 'qty': 2, 'price': 100},
            {'name': 'B', 'qty': 1, 'price': 50.5},
        ]
    }

    result, total = build_calculation_result(payload)

    assert total == 250.5
    assert result['items_count'] == 2
    assert result['items'][0]['subtotal'] == 200.0
