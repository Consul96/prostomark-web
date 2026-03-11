def build_calculation_result(input_json: dict) -> tuple[dict, float]:
    items = input_json.get('items', []) if isinstance(input_json, dict) else []
    total = 0.0
    normalized_items: list[dict] = []

    for item in items:
        qty = float(item.get('qty', 0) or 0)
        price = float(item.get('price', 0) or 0)
        subtotal = round(qty * price, 2)
        total += subtotal
        normalized_items.append(
            {
                'name': item.get('name', ''),
                'qty': qty,
                'price': price,
                'subtotal': subtotal,
            }
        )

    result = {
        'items': normalized_items,
        'total': round(total, 2),
        'items_count': len(normalized_items),
    }
    return result, round(total, 2)
