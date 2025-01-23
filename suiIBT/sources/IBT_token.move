module 0x0::ibt {
    use sui::coin;
    use sui::tx_context;
    use sui::transfer;
    use std::option;

    // Struct representing the IBT token
    public struct IBT has drop {}

    // Initialize the IBT token
    fun init(witness: IBT, ctx: &mut tx_context::TxContext) {
        let (treasury_cap, metadata) = coin::create_currency(witness, 18, b"IBT", b"IBT Token", b"", option::none(), ctx);
        transfer::public_transfer(treasury_cap, tx_context::sender(ctx));
        transfer::public_transfer(metadata, tx_context::sender(ctx));
    }

    // Mint new IBT tokens
    public entry fun mint(treasury_cap: &mut coin::TreasuryCap<IBT>, amount: u64, recipient: address, ctx: &mut tx_context::TxContext) {
        let coins = coin::mint(treasury_cap, amount, ctx);
        transfer::public_transfer(coins, recipient);
    }

    // Burn IBT tokens
    public entry fun burn(treasury_cap: &mut coin::TreasuryCap<IBT>, coins: coin::Coin<IBT>) {
        coin::burn(treasury_cap, coins);
    }
}