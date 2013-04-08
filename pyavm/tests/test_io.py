import os
import glob
import pytest

try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        pytest.skip()

try:
    import numpy as np
except ImportError:
    pytest.skip()

from .. import AVM


@pytest.mark.parametrize('xml_file', glob.glob(os.path.join('data', '*.xml')))
def test_io_jpg(tmpdir, xml_file):
    avm = AVM()
    avm.from_xml_file(xml_file)
    filename_in = tmpdir.join('test_in.png').strpath
    filename_out = tmpdir.join('test_out.png').strpath
    i = Image.fromarray(np.ones((16, 16), dtype=np.uint8))
    i.save(filename_in)
    avm.embed(filename_in, filename_out, verify=True)