from scripts.helpful_scripts import get_account
from brownie import interface, config, network, web3
from web3 import Web3


def main():
    get_weth()


def get_weth():
    """
    Mint Weth from ETH
    """
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"]
    )  # abi and address
    tx = weth.deposit({"from": account, "value": 6 * 10 ** 18})
    tx.wait(1)
    print("Received 6 Weth")
    print("Balance: ", Web3.fromWei(weth.balanceOf(account.address), "ether"))
    return tx


def withdraw_eth():
    """
    Withdraw ETH and burn WETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(0.1 * 10 ** 18, {"from": account})
    tx.wait(1)
    print("0.1 ETH withdrawn")
    return tx
