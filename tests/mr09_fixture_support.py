"""Capability handling for optional MR09 symbolic-link test fixtures."""
import os
from unittest import SkipTest


def symlink_or_skip(link, target):
    """Skip only Windows' explicit missing-symbolic-link-privilege condition."""
    try:
        link.symlink_to(target)
    except OSError as error:
        if os.name == "nt" and getattr(error, "winerror", None) == 1314:
            raise SkipTest("symbolic-link fixture unavailable "
                           "(Windows privilege not held; winerror 1314)") from error
        raise
