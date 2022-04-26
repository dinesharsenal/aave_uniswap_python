from brownie import chain, config, network, interface
import brownie
from pyrsistent import immutable
from scripts.helpful_scripts import (
    get_account,
    getPriceFeed,
    getBorrowableEth,
    getLendingPool,
    approveErc20,
    repayAll,
    swap,
)
from scripts.get_weth import get_weth, withdraw_eth
from web3 import Web3
import time

amount = Web3.toWei(5, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in "mainnet-fork":
        get_weth()
    lending_pool = getLendingPool()

    approve_tx = approveErc20(lending_pool.address, amount, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address,
        amount,
        account.address,
        0,
        {"from": account},
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = getBorrowableEth(lending_pool, account)
    print("Let's borrow some DAI")
    getPriceFeed()
    # Dai in terms of eth
    borrowable_dai = (1 / getPriceFeed()) * borrowable_eth * 0.95
    print("Borrowable DAI is ", borrowable_dai)
    tx = lending_pool.borrow(
        config["networks"][network.show_active()]["dai_token"],
        Web3.toWei(borrowable_dai, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    tx.wait(1)
    print("Borrowed!")
    print(getBorrowableEth(lending_pool, account))
    # We got some borrowed DAI
    # Short selling/Selling on margin
    print("Starting swap")
    tokenIn = config["networks"][network.show_active()]["dai_token"]
    tokenOut = config["networks"][network.show_active()]["weth_token"]
    path = [tokenIn, tokenOut]
    swap_router = interface.IUniswapV2Router02(
        config["networks"][network.show_active()]["swap_adddress_v2"]
    )
    approveErc20(
        swap_router.address, Web3.toWei(borrowable_dai, "ether"), tokenIn, account
    )
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    dai = interface.IERC20(config["networks"][network.show_active()]["dai_token"])
    print("Weth Balance before Swap:", weth.balanceOf(account.address))
    print("Dai Balance before Swap: ", dai.balanceOf(account.address))
    swap(swap_router, path, account, Web3.toWei(borrowable_dai, "ether"))
    print("Weth Balance after Swap: ", weth.balanceOf(account.address))
    print("Dai Balance after Swap: ", dai.balanceOf(account.address))
