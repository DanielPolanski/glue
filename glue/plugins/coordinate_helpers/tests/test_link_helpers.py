from __future__ import absolute_import, division, print_function

import pytest
import numpy as np

pytest.importorskip('astropy')

from glue.core import ComponentID
from glue.core.tests.test_link_helpers import check_link, check_using
from glue.core.tests.test_state import clone

from ..link_helpers import (Galactic_to_FK5, FK4_to_FK5, ICRS_to_FK5,
                            Galactic_to_FK4, ICRS_to_FK4, ICRS_to_Galactic,
                            GalactocentricToGalactic)

# We now store for each class the expected result of the conversion of (45,50)
# from the input frame to output frame and then from the output frame to the
# input frame.
EXPECTED = {
    Galactic_to_FK5: [(238.23062386, 27.96352696), (143.12136866, -7.76422226)],
    FK4_to_FK5: [(45.87780898, 50.19529421), (44.12740884, 49.80169907)],
    ICRS_to_FK5: [(45.00001315, 49.99999788), (44.99998685, 50.00000212)],
    Galactic_to_FK4: [(237.71557513, 28.11113265), (143.52337155, -7.32105993)],
    ICRS_to_FK4: [(44.12742195, 49.801697), (45.87779583, 50.19529642)],
    ICRS_to_Galactic: [(143.12137717, -7.76422008), (238.23062019, 27.96352359)],
}

lon1, lat1, lon2, lat2 = (ComponentID('lon_in'), ComponentID('lat_in'),
                          ComponentID('lon_out'), ComponentID('lat_out'))


@pytest.mark.parametrize(('conv_class', 'expected'), list(EXPECTED.items()))
def test_conversion(conv_class, expected):

    result = conv_class([lon1, lat1], [lon2, lat2])

    assert len(result) == 4

    # Check links are correct
    check_link(result[0], [lon1, lat1], lon2)
    check_link(result[1], [lon1, lat1], lat2)
    check_link(result[2], [lon2, lat2], lon1)
    check_link(result[3], [lon2, lat2], lat1)

    # Check string representation
    assert str(result[0]) == "lon_out <- " + conv_class.__name__ + ".forwards_1(lon_in, lat_in)"
    assert str(result[1]) == "lat_out <- " + conv_class.__name__ + ".forwards_2(lon_in, lat_in)"
    assert str(result[2]) == "lon_in <- " + conv_class.__name__ + ".backwards_1(lon_out, lat_out)"
    assert str(result[3]) == "lat_in <- " + conv_class.__name__ + ".backwards_2(lon_out, lat_out)"

    # Check numerical accuracy

    x = np.array([45])
    y = np.array([50])

    check_using(result[0], (x, y), expected[0][0])
    check_using(result[1], (x, y), expected[0][1])
    check_using(result[2], (x, y), expected[1][0])
    check_using(result[3], (x, y), expected[1][1])

    # Check that state saving works

    check_using(clone(result[0]), (x, y), expected[0][0])
    check_using(clone(result[1]), (x, y), expected[0][1])
    check_using(clone(result[2]), (x, y), expected[1][0])
    check_using(clone(result[3]), (x, y), expected[1][1])


x, y, z, l, b, d = (ComponentID('x'), ComponentID('y'), ComponentID('z'),
                    ComponentID('l'), ComponentID('b'), ComponentID('d'))


def test_galactocentric():

    result = GalactocentricToGalactic([x, y, z], [l, b, d])

    assert len(result) == 6

    # Check links are correct
    check_link(result[0], [x, y, z], l)
    check_link(result[1], [x, y, z], b)
    check_link(result[2], [x, y, z], d)
    check_link(result[3], [l, b, d], x)
    check_link(result[4], [l, b, d], y)
    check_link(result[5], [l, b, d], z)

    # Check string representation
    assert str(result[0]) == "l <- GalactocentricToGalactic.forwards_1(x, y, z)"
    assert str(result[1]) == "b <- GalactocentricToGalactic.forwards_2(x, y, z)"
    assert str(result[2]) == "d <- GalactocentricToGalactic.forwards_3(x, y, z)"
    assert str(result[3]) == "x <- GalactocentricToGalactic.backwards_1(l, b, d)"
    assert str(result[4]) == "y <- GalactocentricToGalactic.backwards_2(l, b, d)"
    assert str(result[5]) == "z <- GalactocentricToGalactic.backwards_3(l, b, d)"

    # Check numerical accuracy

    ref = (1., 1., 2.)

    check_using(result[0], ref, 6.141592406648453)
    check_using(result[1], ref, 12.096336453181067)
    check_using(result[2], ref, 9.559388692193782)
    check_using(result[3], ref, -6.30046229834067)
    check_using(result[4], ref, 0.03489758558640843)
    check_using(result[5], ref, 0.055403498825152414)

    # Check that state saving works

    check_using(clone(result[0]), ref, 6.141592406648453)
    check_using(clone(result[1]), ref, 12.096336453181067)
    check_using(clone(result[2]), ref, 9.559388692193782)
    check_using(clone(result[3]), ref, -6.30046229834067)
    check_using(clone(result[4]), ref, 0.03489758558640843)
    check_using(clone(result[5]), ref, 0.055403498825152414)
