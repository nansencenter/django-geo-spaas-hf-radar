def as_dict(value=None, unit=None, f_field=None):
    """Create a dictionary from input pair key-value"""

    return {
        'value': value,
        'units': unit,
        'file field': f_field
    }


def month_to_int(m_name):
    """Convert a month form a full name to int"""

    months_db = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
    }

    return months_db[m_name]

