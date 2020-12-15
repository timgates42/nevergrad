# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from unittest import SkipTest
import pytest
import numpy as np
from . import core
from nevergrad.optimization.optimizerlib import OnePlusOne


@pytest.mark.parametrize("fid", range(1, 24))  # type: ignore
def test_PBO(fid: int) -> None:
    try:
        func = core.PBOFunction(fid, 0, 16)
    except ModuleNotFoundError:
        raise SkipTest("IOH is not installed")
    values = []
    for _ in range(30):
        x = func.parametrization.sample()
        for i in range(len(x.value)):
            assert x.value[i] == 0 or x.value[i] == 1, f"Non binary sample {x}."
        value = func(x.value)
        assert isinstance(value, float), "All output of the iohprofiler-functions should be float"
        assert np.isfinite(value)
        values.append(value)
    optim = OnePlusOne(func.parametrization, budget=100)
    recom = optim.minimize(func)
    values.append(func(recom.value))  # type: ignore
    assert (
        fid in [19, 20, 21, 22, 23] or min(values) >= 0.0 or max(values) <= 0.0
    ), f"IOH profile functions should have constant sign: pb with fid={fid}."



@pytest.mark.parametrize("instrumentation", ["Softmax", "Ordered"])  # type: ignore
def test_PBO_parameterization(instrumentation: str) -> None:
    try:
        func = core.PBOFunction(1, 0, 16, instrumentation=instrumentation)
    except ModuleNotFoundError:
        raise SkipTest("IOH is not installed")
    x = func.parametrization.sample()
    value = func(x.value)
    assert isinstance(value, float), "All output of the iohprofiler-functions should be float"
    assert np.isfinite(value)


def test_W_model() -> None:
    try:
        func = core.WModelFunction()
    except ModuleNotFoundError:
        raise SkipTest("IOH is not installed")
    x = func.parametrization.sample()
    func2 = core.PBOFunction(1, 0, 16)
    assert func(x.value) == func2(x.value), "W-model with default setting should equal base_function"
    func = core.WModelFunction(base_function="LeadingOnes")
    x = func.parametrization.sample()
    func2 = core.PBOFunction(2, 0, 16)
    assert func(x.value) == func2(x.value), "W-model with default setting should equal base_function"
