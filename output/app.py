import gradio as gr
import time
from accounts import Account, get_share_price

# Initialize a global account object with None
current_account = None

def create_account(initial_deposit):
    global current_account
    try:
        initial_deposit = float(initial_deposit)
        current_account = Account(initial_deposit)
        return f"Account created with initial deposit of ${initial_deposit:.2f}", get_account_info()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def deposit_funds(amount):
    if not current_account:
        return "Error: No account exists. Create an account first.", ""
    
    try:
        amount = float(amount)
        current_account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}", get_account_info()
    except ValueError as e:
        return f"Error: {str(e)}", get_account_info()

def withdraw_funds(amount):
    if not current_account:
        return "Error: No account exists. Create an account first.", ""
    
    try:
        amount = float(amount)
        current_account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}", get_account_info()
    except ValueError as e:
        return f"Error: {str(e)}", get_account_info()

def buy_shares(symbol, quantity):
    if not current_account:
        return "Error: No account exists. Create an account first.", ""
    
    try:
        symbol = symbol.upper().strip()
        quantity = int(quantity)
        current_price = get_share_price(symbol)
        current_account.buy_shares(symbol, quantity)
        return f"Successfully bought {quantity} shares of {symbol} at ${current_price:.2f} per share", get_account_info()
    except ValueError as e:
        return f"Error: {str(e)}", get_account_info()

def sell_shares(symbol, quantity):
    if not current_account:
        return "Error: No account exists. Create an account first.", ""
    
    try:
        symbol = symbol.upper().strip()
        quantity = int(quantity)
        current_price = get_share_price(symbol)
        current_account.sell_shares(symbol, quantity)
        return f"Successfully sold {quantity} shares of {symbol} at ${current_price:.2f} per share", get_account_info()
    except ValueError as e:
        return f"Error: {str(e)}", get_account_info()

def get_account_info():
    if not current_account:
        return "No account exists. Create an account first."
    
    portfolio_value = current_account.calculate_portfolio_value()
    profit_or_loss = current_account.calculate_profit_or_loss()
    holdings = current_account.list_holdings()
    
    info = f"Account Summary\n"
    info += f"--------------\n"
    info += f"Cash Balance: ${current_account.balance:.2f}\n"
    info += f"Portfolio Value: ${portfolio_value:.2f}\n"
    
    if profit_or_loss >= 0:
        info += f"Profit: ${profit_or_loss:.2f}\n"
    else:
        info += f"Loss: ${-profit_or_loss:.2f}\n"
    
    info += f"\nCurrent Holdings\n"
    info += f"---------------\n"
    
    if holdings:
        for symbol, quantity in holdings.items():
            price = get_share_price(symbol)
            value = price * quantity
            info += f"{symbol}: {quantity} shares at ${price:.2f} = ${value:.2f}\n"
    else:
        info += "No stock holdings.\n"
    
    return info

def get_transactions_list():
    if not current_account:
        return "No account exists. Create an account first."
    
    transactions = current_account.list_transactions()
    
    if not transactions:
        return "No transactions found."
    
    info = "Transaction History\n"
    info += "------------------\n"
    
    for transaction in transactions:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(transaction['timestamp']))
        
        if transaction['type'] == "DEPOSIT":
            info += f"{timestamp} - DEPOSIT: ${transaction['amount']:.2f}\n"
        
        elif transaction['type'] == "WITHDRAW":
            info += f"{timestamp} - WITHDRAW: ${transaction['amount']:.2f}\n"
        
        elif transaction['type'] == "BUY":
            info += f"{timestamp} - BUY: {transaction['quantity']} shares of {transaction['symbol']} at ${transaction['price']:.2f} (Total: ${transaction['amount']:.2f})\n"
        
        elif transaction['type'] == "SELL":
            info += f"{timestamp} - SELL: {transaction['quantity']} shares of {transaction['symbol']} at ${transaction['price']:.2f} (Total: ${transaction['amount']:.2f})\n"
    
    return info

def get_available_stocks():
    return """Available Stocks for Demo:
- AAPL ($150.00)
- TSLA ($250.00)
- GOOGL ($120.00)"""

with gr.Blocks(title="Trading Simulation Platform") as app:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("A simple account management system for trading simulation.")
    
    with gr.Tab("Account Management"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Create Account")
                initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
                create_button = gr.Button("Create Account")
                
                gr.Markdown("## Deposit Funds")
                deposit_input = gr.Textbox(label="Deposit Amount ($)")
                deposit_button = gr.Button("Deposit")
                
                gr.Markdown("## Withdraw Funds")
                withdraw_input = gr.Textbox(label="Withdraw Amount ($)")
                withdraw_button = gr.Button("Withdraw")
                
                message_output = gr.Textbox(label="Message", lines=2)
            
            with gr.Column():
                account_info = gr.Textbox(label="Account Information", lines=15)
                refresh_button = gr.Button("Refresh Account Info")
    
    with gr.Tab("Trading"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Buy Shares")
                buy_symbol_input = gr.Textbox(label="Stock Symbol")
                buy_quantity_input = gr.Textbox(label="Quantity")
                buy_button = gr.Button("Buy Shares")
                
                gr.Markdown("## Sell Shares")
                sell_symbol_input = gr.Textbox(label="Stock Symbol")
                sell_quantity_input = gr.Textbox(label="Quantity")
                sell_button = gr.Button("Sell Shares")
                
                trade_message_output = gr.Textbox(label="Message", lines=2)
                
                gr.Markdown("## Available Stocks (Demo)")
                stocks_info = gr.Textbox(value=get_available_stocks(), label="Available Stocks", lines=4)
            
            with gr.Column():
                trading_account_info = gr.Textbox(label="Account Information", lines=15)
    
    with gr.Tab("Transaction History"):
        transactions_output = gr.Textbox(label="Transactions", lines=20)
        view_transactions_button = gr.Button("View Transactions")
    
    # Event handlers for account management
    create_button.click(
        create_account,
        inputs=initial_deposit_input,
        outputs=[message_output, account_info]
    )
    
    deposit_button.click(
        deposit_funds,
        inputs=deposit_input,
        outputs=[message_output, account_info]
    )
    
    withdraw_button.click(
        withdraw_funds,
        inputs=withdraw_input,
        outputs=[message_output, account_info]
    )
    
    refresh_button.click(
        lambda: (get_account_info()),
        inputs=None,
        outputs=account_info
    )
    
    # Event handlers for trading
    buy_button.click(
        buy_shares,
        inputs=[buy_symbol_input, buy_quantity_input],
        outputs=[trade_message_output, trading_account_info]
    )
    
    sell_button.click(
        sell_shares,
        inputs=[sell_symbol_input, sell_quantity_input],
        outputs=[trade_message_output, trading_account_info]
    )
    
    # Event handler for transaction history
    view_transactions_button.click(
        get_transactions_list,
        inputs=None,
        outputs=transactions_output
    )

if __name__ == "__main__":
    app.launch()