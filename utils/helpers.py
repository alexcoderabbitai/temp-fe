def str_to_bool(bool_str):
    """
    Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1';
    False values are 'n', 'no', 'f', 'false', 'off', and '0'.
    Raises ValueError if 'bool_str' is anything else.
    Case insensitive.
    """
    bool_str = bool_str.lower()
    if bool_str in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif bool_str in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"Invalid truth value: '{bool_str}'")
