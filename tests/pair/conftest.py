import os
from datetime import timedelta
from math import log
from typing import Any, Callable, List

import boa
import pytest
from hypothesis import settings

boa.reset_env()

@pytest.fixture(scope="session")
def accounts() -> List[Any]:
    return [boa.env.generate_address() for _ in range(10)]

@pytest.fixture(scope="session")
def account(accounts) -> Any:
    return accounts[0]

@pytest.fixture(scope="session")
def get_collateral_token(account) -> Callable[[int], Any]:
    def f(digits):
        with boa.env.prank(account):
            return boa.load('vyper_contracts/mocks/mock_erc20.vy', "Collateral", "CTL", digits)
    return f

@pytest.fixture(scope="session")
def get_asset_token(account) -> Callable[[int], Any]:
    def f(digits):
        with boa.env.prank(account):
            return boa.load('vyper_contracts/mocks/mock_erc20.vy', "Asset", "ASS", digits)
    return f

@pytest.fixture(scope="session")
def collateral(get_collateral_token):
    return get_collateral_token(18)

@pytest.fixture(scope="session")
def asset(get_asset_token):
    return get_asset_token(18)

@pytest.fixture(scope="session")
def oracle(account):
    with boa.env.prank(account):
        oracle = boa.load('vyper_contracts/mocks/mock_oracle.vy')
        return oracle
    
@pytest.fixture(scope="session")
def cog_pair_blueprint(account):
    pair = boa.load_partial('vyper_contracts/cog_pair.vy')
    with boa.env.prank(account):
        return pair.deploy_as_blueprint()

@pytest.fixture(scope="session")
def cog_factory(account, cog_pair_blueprint):
    with boa.env.prank(account):
        factory = boa.load('vyper_contracts/cog_factory.vy', cog_pair_blueprint, account)
        return factory

@pytest.fixture(scope="session")
def cog_pair(account, cog_factory, oracle, asset, collateral):
    with boa.env.prank(account):
        pair = boa.load_partial('vyper_contracts/cog_pair.vy')
        return pair.at(cog_factory.deploy_medium_risk_pair(asset, collateral, oracle))

@pytest.fixture(scope="session")
def tick_math(account):
    with boa.env.prank(account):
        math = boa.load('vyper_contracts/mocks/mock_tick_math.vy')
        return math