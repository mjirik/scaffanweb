import pytest
import scaffanweb
import microimprocessing.scaffanweb_tools

def test_sha():
    st = microimprocessing.scaffanweb_tools.generate_sha1("asdf","123")
    print(st)
    pass
