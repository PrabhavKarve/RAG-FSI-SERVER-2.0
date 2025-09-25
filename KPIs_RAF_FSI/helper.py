def _need(df, key, col):
    """Strict access; raises clear error if missing."""
    try:
        val = df.at[key, col]
    except KeyError as e:
        raise KeyError(f"Missing required line_item '{key}' for {col}") from e
    if val is None:
        raise ValueError(f"line_item '{key}' returned None for {col}")
    return float(val)

def _opt(df, key, col, default=0.0):
    """Optional access; returns default if missing/None."""
    try:
        val = df.at[key, col]
        return default if val is None else float(val)
    except KeyError:
        return default
