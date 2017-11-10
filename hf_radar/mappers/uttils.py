def as_dict(value=None, unit=None, f_field=None):
    """Create a dictionary from input pair key-value"""

    return {
        'value': value,
        'units': unit,
        'file field': f_field
    }
