def get_data_as_dictionary(elems: list) -> list:
    if not elems: return

    container = []
    for e in elems:
        container.append(e.to_dict())
    return container