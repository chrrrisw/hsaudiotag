# Created By: Chris Willoughby
# Created On: 2016/04/12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..util import x_from_x_of_y
from .util import eq_

def test_x_from_x_of_y():
    eq_(34, x_from_x_of_y(34))
    eq_(42, x_from_x_of_y('42'))
    eq_(0, x_from_x_of_y(''))
    eq_(12, x_from_x_of_y('12/24'))
    eq_(0, x_from_x_of_y(' '))
    eq_(0, x_from_x_of_y('/'))
    eq_(0, x_from_x_of_y('foo/12'))
