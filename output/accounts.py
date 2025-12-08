def get_share_price(symbol):
    """Returns the current price of a share for testing purposes.
    
    Args:
        symbol (str): The stock symbol to get the price for.
        
    Returns:
        float: The current price of the share.
    """
    # This is a test implementation that returns fixed prices for common symbols
    prices = {
        'AAPL': 150.0,
        'TSLA': 250.0,
        'GOOGL': 120.0
    }
    if symbol in prices:
        return prices[symbol]
    else:
        raise ValueError(f"Price for symbol '{symbol}' not available")


class Account:
    """Represents a user's trading account for a trading simulation platform."""
    
    def __init__(self, initial_deposit):
        """Initialize a new account with an initial deposit.
        
        Args:
            initial_deposit (float): The initial amount deposited into the account.
            
        Raises:
            ValueError: If the initial deposit is not positive.
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be positive")
        
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.holdings = {}
        self.transactions = []
        
        # Record the initial deposit as a transaction
        self._record_transaction("DEPOSIT", initial_deposit)
    
    def _record_transaction(self, transaction_type, amount, symbol=None, quantity=None, price=None):
        """Record a transaction in the transactions list.
        
        Args:
            transaction_type (str): The type of transaction (DEPOSIT, WITHDRAW, BUY, SELL).
            amount (float): The amount involved in the transaction.
            symbol (str, optional): The stock symbol for buy/sell transactions.
            quantity (int, optional): The quantity of shares for buy/sell transactions.
            price (float, optional): The price per share for buy/sell transactions.
        """
        import time
        
        transaction = {
            'timestamp': time.time(),
            'type': transaction_type,
            'amount': amount
        }
        
        if symbol is not None:
            transaction['symbol'] = symbol
        
        if quantity is not None:
            transaction['quantity'] = quantity
            
        if price is not None:
            transaction['price'] = price
        
        self.transactions.append(transaction)
    
    def deposit(self, amount):
        """Deposit funds into the account.
        
        Args:
            amount (float): The amount to deposit.
            
        Raises:
            ValueError: If the deposit amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self._record_transaction("DEPOSIT", amount)
    
    def withdraw(self, amount):
        """Withdraw funds from the account.
        
        Args:
            amount (float): The amount to withdraw.
            
        Raises:
            ValueError: If the withdrawal amount is not positive or would result in a negative balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal")
        
        self.balance -= amount
        self._record_transaction("WITHDRAW", amount)
    
    def buy_shares(self, symbol, quantity):
        """Buy shares of a specified stock.
        
        Args:
            symbol (str): The stock symbol to buy.
            quantity (int): The quantity of shares to buy.
            
        Raises:
            ValueError: If the quantity is not positive or if there are insufficient funds.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Get the current price of the stock
        price = get_share_price(symbol)
        
        # Calculate the total cost
        cost = price * quantity
        
        # Check if there are sufficient funds
        if cost > self.balance:
            raise ValueError("Insufficient funds to buy shares")
        
        # Update the balance
        self.balance -= cost
        
        # Update the holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        
        # Record the transaction
        self._record_transaction("BUY", cost, symbol, quantity, price)
    
    def sell_shares(self, symbol, quantity):
        """Sell shares of a specified stock.
        
        Args:
            symbol (str): The stock symbol to sell.
            quantity (int): The quantity of shares to sell.
            
        Raises:
            ValueError: If the quantity is not positive or if there are insufficient shares.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if the user has the shares
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell")
        
        # Get the current price of the stock
        price = get_share_price(symbol)
        
        # Calculate the total proceeds
        proceeds = price * quantity
        
        # Update the balance
        self.balance += proceeds
        
        # Update the holdings
        self.holdings[symbol] -= quantity
        
        # Remove the symbol from holdings if the quantity is 0
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record the transaction
        self._record_transaction("SELL", proceeds, symbol, quantity, price)
    
    def calculate_portfolio_value(self):
        """Calculate the total value of the portfolio (cash + stock holdings).
        
        Returns:
            float: The total portfolio value.
        """
        # Start with the cash balance
        total_value = self.balance
        
        # Add the value of all stock holdings
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        
        return total_value
    
    def calculate_profit_or_loss(self):
        """Calculate the profit or loss from the initial deposit.
        
        Returns:
            float: The profit (positive) or loss (negative) amount.
        """
        return self.calculate_portfolio_value() - self.initial_deposit
    
    def list_holdings(self):
        """Get the current stock holdings.
        
        Returns:
            dict: A dictionary with stock symbols as keys and quantities as values.
        """
        return self.holdings.copy()
    
    def list_transactions(self):
        """Get a list of all transactions made.
        
        Returns:
            list: A list of all transactions.
        """
        return self.transactions.copy()
    
    def calculate_profit_or_loss_at_time(self, timestamp):
        """Calculate the profit or loss at a specific point in time.
        
        Args:
            timestamp (float): The UNIX timestamp to calculate profit/loss at.
            
        Returns:
            float: The profit (positive) or loss (negative) amount at the given time.
        """
        # Replay all transactions up to the given timestamp
        balance = 0
        holdings = {}
        initial_deposit = None
        
        for transaction in self.transactions:
            if transaction['timestamp'] > timestamp:
                break
            
            if transaction['type'] == "DEPOSIT":
                balance += transaction['amount']
                if initial_deposit is None:  # The first deposit is the initial deposit
                    initial_deposit = transaction['amount']
            
            elif transaction['type'] == "WITHDRAW":
                balance -= transaction['amount']
            
            elif transaction['type'] == "BUY":
                balance -= transaction['amount']
                symbol = transaction['symbol']
                quantity = transaction['quantity']
                
                if symbol in holdings:
                    holdings[symbol] += quantity
                else:
                    holdings[symbol] = quantity
            
            elif transaction['type'] == "SELL":
                balance += transaction['amount']
                symbol = transaction['symbol']
                quantity = transaction['quantity']
                
                holdings[symbol] -= quantity
                
                if holdings[symbol] == 0:
                    del holdings[symbol]
        
        # Calculate the total value at the given time
        total_value = balance
        for symbol, quantity in holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        
        return total_value - initial_deposit