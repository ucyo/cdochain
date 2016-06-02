#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""Tests for chaining module."""

import pytest
from cdochain import exceptions as ex
from cdochain import helpers as hlp
import cdochain.chaining as cch
import cdo
import netCDF4 as ncd
import numpy as np
import os


class Test_Calculations(object):
    """Test of proper calculations and workings."""

    def setup(self):
        """Setup process."""
        self.ifile = './test/testdata/sresa1b_ncar_ccsm3-example.nc'
        cdomethods = cdo.Cdo()
        self.tmp_iter = cdomethods.mermean(input=self.ifile,
                                           output=self.ifile[:-3]+'-mer.nc',
                                           options="-O -f nc")
        self.final = cdomethods.zonmean(input=self.tmp_iter,
                                        output=self.ifile[:-3]+'-mer-zon.nc',
                                        options="-O -f nc")
        self.data_iter = ncd.Dataset(self.final)

        tmp_at_one_go = "-mermean "+self.ifile
        self.final_str = cdomethods.zonmean(input=tmp_at_one_go,
                                            output=self.ifile[:-3] +
                                            '-mer-zon-str.nc')
        self.datas = ncd.Dataset(self.final_str)
        self.sellev = cdomethods.sellevidx(12, input=self.ifile,
                                           output=self.ifile[:-3]+'-lvl12.nc',
                                           options="-O -f nc")

    def teardown(self):
        """Teardown process."""
        os.remove(self.tmp_iter)
        os.remove(self.final)
        os.remove(self.final_str)
        os.remove(self.sellev)

    def test_selarg(self):
        """Test chaining with arguments."""
        routine = cch.Chain(self.ifile, self.ifile[:-3]+'seltest.nc')
        sellvl12 = routine.sellevidx(12)
        res = sellvl12.execute()
        assert np.array_equal(ncd.Dataset(res)['ua'][:],
                              ncd.Dataset(self.sellev)['ua'][:])
        os.remove(res)

    def test_setup(self):
        """Test if setup was successfull."""
        assert np.array_equal(self.data_iter['tas'][:], self.datas['tas'][:])

    def test_single_concatination(self):
        """Test if cdochain works with only one input."""
        routine = cch.Chain(self.ifile, self.tmp_iter[:-3]+'-mer-ch.nc')
        meridian = routine.mermean().zonmean()
        res = meridian.execute()
        assert np.array_equal(ncd.Dataset(res)['tas'][:],
                              self.data_iter['tas'][:])
        os.remove(res)

    def test_str_format(self):
        """Testing successfull string formation."""
        routine = cch.Chain(self.ifile, self.ifile[:-3]+'str_test.nc')
        res = routine.sellevidx(24)
        assert res._last_command.to_cmdstr() == "-sellevidx,24 {}".format(
            self.ifile)

inputs = ['./test/testdata/RC1SD-base-08__201301_ECHAM5_tm1-aps-qm1.nc',
          './test/testdata/RC1SD-base-08__201302_ECHAM5_tm1-aps-qm1.nc',
          './test/testdata/RC1SD-base-08__201303_ECHAM5_tm1-aps-qm1.nc',
          './test/testdata/RC1SD-base-08__201304_ECHAM5_tm1-aps-qm1.nc']


@pytest.mark.slow
@pytest.mark.parametrize("filelist", [inputs])
def test_multiple_files_list(filelist):
    """Test the usage of multiple files as input."""
    out = cch.Chain(ifile=filelist, ofile='./test/testdata/outputs.nc')
    assert out._ifile == '/tmp/outputs.nc'
    os.remove(out._ifile)


@pytest.mark.slow
@pytest.mark.parametrize("filelist",
                         ["./test/testdata/RC1SD-base-08__20130*.nc"])
def test_multiple_files_glob(filelist):
    """Test the usage of multiple files as input."""
    out = cch.Chain(ifile=filelist, ofile='./test/testdata/outputs.nc')
    assert out._ifile == '/tmp/outputs.nc'
    os.remove(out._ifile)


def test_return_types():
    """Test for different return types."""
    assert False


def test_format_inputs():
    """Test if formating of options works."""
    assert hlp.formats(['235', 532, 412]) == '235,532,412'
    assert hlp.formats(('235', 532, 412)) == '235,532,412'
    assert hlp.formats(['ifile', 532, '412']) == 'ifile,532,412'
    assert isinstance(hlp.formats(['ifile', 532, '412']), str)


def test_initializing():
    """Test if initilalisation is working."""
    init = cch.Chain("inputfile", "outputfile", "options")
    assert isinstance(init, cch.Chain)


def test_invalid_method():
    """Test if invalid input raises proper exception."""
    init = cch.Chain("inputfile", "outputfile", "options")
    with pytest.raises(ex.InvalidMethod):
        init.coolmean("32")


def test_valid_method():
    """Test if one valid input is accepted."""
    init = cch.Chain("inputfile", "outputfile", "options")
    init.mermean("32")
