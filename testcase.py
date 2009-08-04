# Created By: Virgil Dupras
# Created On: 2009-05-28
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsutil.testcase import TestCase as TestCaseBase
from hsutil.path import Path

class TestCase(TestCaseBase):
    @classmethod
    def datadirpath(cls):
        return Path(__file__)[:-1] + 'testdata'
    