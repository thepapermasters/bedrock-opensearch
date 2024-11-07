import urllib


def uri_decode(encoded_uri: str) -> str:
    """
    Decodes a given URI-encoded string back to its original form.
    :param encoded_uri: The URI-encoded string.
    :return: Decoded string.
    """
    # Clean file name
    return urllib.parse.unquote_plus(encoded_uri)
