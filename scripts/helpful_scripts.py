from brownie import accounts, network, config, chain, interface
import brownie
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache",
    "hardhat",
    "local-ganache",
    "mainnet-fork",
]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


def repayAll(lending_pool, amount, erc20_address, account):
    approveErc20(lending_pool, amount, erc20_address, account)
    tx = lending_pool.repay(
        erc20_address, amount, 1, account.address, {"from": account}
    )
    tx.wait(1)
    print(lending_pool.getUserAccountData(account.address))
    print("Repaid!")
    print("You just deposited, borrowed and repayed with Aave, Brownie and Chainlink!")
    return tx


def getPriceFeed(token_eth_price_feed=None):
    if not token_eth_price_feed:
        token_eth_contract = interface.AggregatorV3Interface(
            config["networks"][network.show_active()]["dai_eth_price_feed"]
        )
    else:
        token_eth_contract = interface.AggregatorV3Interface(token_eth_price_feed)
    latest_price = token_eth_contract.latestRoundData()[1]
    latest_price = Web3.fromWei(latest_price, "ether")
    return float(latest_price)


def getBorrowableEth(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"Total collateral available is ", totalCollateralETH)
    print(f"Total debt is ", totalDebtETH)
    print(f"You can borrow this much more ETH only=> ", availableBorrowsETH)
    return (float(availableBorrowsETH), float(totalDebtETH))


def approveErc20(spender, amount, erc20_address, account):
    print("Approving...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    print(erc20)
    return tx


def getLendingPool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    print("lending_pool address is: ", lending_pool_address)
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def swap(swap_router, path, account, amount):
    expiry_time = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
    token_eth_price = getPriceFeed()
    amount_out_minimum = amount * (token_eth_price * 0.9)
    tx = swap_router.swapExactTokensForTokensSupportingFeeOnTransferTokens(
        amount,
        0,
        path,
        account.address,
        expiry_time,
        {"from": account},
    )
    tx.wait(1)
    print("Swapped bro chill")
    return tx
