class DecodeFailure(Exception):
    pass


class DecodeFailureHori(DecodeFailure):
    """Decoder Failed due to Horizontal Starting Points Judgement"""
    pass


class DecodeFailureVert(DecodeFailure):
    """Decoder Failed due to Vertical Starting Points Judgement"""
    pass


if "__main__" == __name__:
    try:
        raise DecodeFailureHori
    except DecodeFailure:
        print("caught")
