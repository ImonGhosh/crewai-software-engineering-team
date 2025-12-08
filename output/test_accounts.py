import unittest
from unittest.mock import patch
import time

# Import the module to test
import accounts

class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_existing(self):
        """Test get_share_price with existing symbols."""
        self.assertEqual(accounts.get_share_price('AAPL'), 150.0)
        self.assertEqual(accounts.get_share_price('TSLA'), 250.0)
        self.assertEqual(accounts.get_share_price('GOOGL'), 120.0)
    
    def test_get_share_price_non_existing(self):
        """Test get_share_price with non-existing symbol raises ValueError."""
        with self.assertRaises(ValueError):
            accounts.get_share_price('MSFT')

class TestAccountInitialization(unittest.TestCase):
    def test_init_positive_deposit(self):
        """Test Account initialization with positive deposit."""
        account = accounts.Account(1000.0)
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0]['type'], 'DEPOSIT')
        self.assertEqual(account.transactions[0]['amount'], 1000.0)
    
    def test_init_zero_deposit(self):
        """Test Account initialization with zero deposit raises ValueError."""
        with self.assertRaises(ValueError):
            accounts.Account(0)
    
    def test_init_negative_deposit(self):
        """Test Account initialization with negative deposit raises ValueError."""
        with self.assertRaises(ValueError):
            accounts.Account(-100.0)

class TestAccountDeposit(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    def test_deposit_positive(self):
        """Test deposit with positive amount."""
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]['type'], 'DEPOSIT')
        self.assertEqual(self.account.transactions[-1]['amount'], 500.0)
    
    def test_deposit_zero(self):
        """Test deposit with zero amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.deposit(0)
    
    def test_deposit_negative(self):
        """Test deposit with negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.deposit(-100.0)

class TestAccountWithdraw(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    def test_withdraw_positive_sufficient(self):
        """Test withdraw with positive amount and sufficient balance."""
        self.account.withdraw(300.0)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]['type'], 'WITHDRAW')
        self.assertEqual(self.account.transactions[-1]['amount'], 300.0)
    
    def test_withdraw_zero(self):
        """Test withdraw with zero amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
    
    def test_withdraw_negative(self):
        """Test withdraw with negative amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.withdraw(-100.0)
    
    def test_withdraw_insufficient(self):
        """Test withdraw with insufficient balance raises ValueError."""
        with self.assertRaises(ValueError):
            self.account.withdraw(1500.0)

class TestAccountBuyShares(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_positive_sufficient(self, mock_get_price):
        """Test buy_shares with positive quantity and sufficient funds."""
        mock_get_price.return_value = 150.0  # AAPL price
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.balance, 1000.0 - (150.0 * 2))  # 700.0
        self.assertEqual(self.account.holdings, {'AAPL': 2})
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]['type'], 'BUY')
        self.assertEqual(self.account.transactions[-1]['amount'], 300.0)
        self.assertEqual(self.account.transactions[-1]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[-1]['quantity'], 2)
        self.assertEqual(self.account.transactions[-1]['price'], 150.0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_zero_quantity(self, mock_get_price):
        """Test buy_shares with zero quantity raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_negative_quantity(self, mock_get_price):
        """Test buy_shares with negative quantity raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -1)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_insufficient_funds(self, mock_get_price):
        """Test buy_shares with insufficient funds raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 10)  # Cost 1500 > balance 1000
    
    @patch('accounts.get_share_price')
    def test_buy_shares_multiple_symbols(self, mock_get_price):
        """Test buying shares of multiple symbols."""
        def side_effect(symbol):
            if symbol == 'AAPL':
                return 150.0
            elif symbol == 'TSLA':
                return 250.0
        mock_get_price.side_effect = side_effect
        self.account.buy_shares('AAPL', 2)  # Cost 300
        self.account.buy_shares('TSLA', 1)  # Cost 250
        self.assertEqual(self.account.balance, 1000.0 - 300.0 - 250.0)  # 450.0
        self.assertEqual(self.account.holdings, {'AAPL': 2, 'TSLA': 1})
    
    @patch('accounts.get_share_price')
    def test_buy_shares_existing_symbol(self, mock_get_price):
        """Test buying additional shares of an existing symbol."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 2)
        self.account.buy_shares('AAPL', 1)
        self.assertEqual(self.account.holdings, {'AAPL': 3})

class TestAccountSellShares(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
        # Pre-buy some shares for selling tests
        with patch('accounts.get_share_price', return_value=150.0):
            self.account.buy_shares('AAPL', 5)  # Cost 750, balance 250
    
    @patch('accounts.get_share_price')
    def test_sell_shares_positive_sufficient(self, mock_get_price):
        """Test sell_shares with positive quantity and sufficient shares."""
        mock_get_price.return_value = 150.0
        self.account.sell_shares('AAPL', 2)
        self.assertEqual(self.account.balance, 250.0 + (150.0 * 2))  # 550.0
        self.assertEqual(self.account.holdings, {'AAPL': 3})
        self.assertEqual(len(self.account.transactions), 3)  # Initial deposit, buy, sell
        self.assertEqual(self.account.transactions[-1]['type'], 'SELL')
        self.assertEqual(self.account.transactions[-1]['amount'], 300.0)
        self.assertEqual(self.account.transactions[-1]['symbol'], 'AAPL')
        self.assertEqual(self.account.transactions[-1]['quantity'], 2)
        self.assertEqual(self.account.transactions[-1]['price'], 150.0)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_zero_quantity(self, mock_get_price):
        """Test sell_shares with zero quantity raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_negative_quantity(self, mock_get_price):
        """Test sell_shares with negative quantity raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -1)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_insufficient_shares(self, mock_get_price):
        """Test sell_shares with insufficient shares raises ValueError."""
        mock_get_price.return_value = 150.0
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 10)  # Only have 5
    
    @patch('accounts.get_share_price')
    def test_sell_shares_nonexistent_symbol(self, mock_get_price):
        """Test sell_shares with symbol not in holdings raises ValueError."""
        mock_get_price.return_value = 250.0
        with self.assertRaises(ValueError):
            self.account.sell_shares('TSLA', 1)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_all_shares(self, mock_get_price):
        """Test selling all shares removes symbol from holdings."""
        mock_get_price.return_value = 150.0
        self.account.sell_shares('AAPL', 5)
        self.assertEqual(self.account.balance, 1000.0)  # Back to initial
        self.assertEqual(self.account.holdings, {})
    
    @patch('accounts.get_share_price')
    def test_sell_shares_multiple_symbols(self, mock_get_price):
        """Test selling shares from multiple symbols."""
        # Reset account with more balance
        self.account = accounts.Account(2000.0)
        # Buy AAPL and TSLA
        with patch('accounts.get_share_price', side_effect=lambda s: 150.0 if s == 'AAPL' else 250.0):
            self.account.buy_shares('AAPL', 5)  # Cost 750
            self.account.buy_shares('TSLA', 2)  # Cost 500
        # Now sell some
        mock_get_price.side_effect = lambda s: 150.0 if s == 'AAPL' else 250.0
        self.account.sell_shares('AAPL', 2)
        self.account.sell_shares('TSLA', 1)
        self.assertEqual(self.account.holdings, {'AAPL': 3, 'TSLA': 1})

class TestAccountPortfolioValue(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_portfolio_value_cash_only(self, mock_get_price):
        """Test portfolio value with only cash."""
        mock_get_price.return_value = 150.0
        self.assertEqual(self.account.calculate_portfolio_value(), 1000.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_portfolio_value_with_holdings(self, mock_get_price):
        """Test portfolio value with cash and holdings."""
        def side_effect(symbol):
            if symbol == 'AAPL':
                return 150.0
            elif symbol == 'TSLA':
                return 250.0
        mock_get_price.side_effect = side_effect
        with patch('accounts.get_share_price', side_effect=side_effect):
            self.account.buy_shares('AAPL', 2)  # Cost 300, balance 700
            self.account.buy_shares('TSLA', 1)  # Cost 250, balance 450
        # Portfolio value = cash 450 + AAPL 2*150=300 + TSLA 1*250=250 = 1000
        self.assertEqual(self.account.calculate_portfolio_value(), 1000.0)

class TestAccountProfitOrLoss(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_no_trades(self, mock_get_price):
        """Test profit/loss with no trades (should be zero)."""
        mock_get_price.return_value = 150.0
        self.assertEqual(self.account.calculate_profit_or_loss(), 0.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_profit(self, mock_get_price):
        """Test profit/loss with profit scenario."""
        # Simulate buying low, price increases
        mock_get_price.return_value = 100.0  # Lower price for buying
        self.account.buy_shares('AAPL', 5)  # Cost 500, balance 500
        mock_get_price.return_value = 150.0  # Price increases for valuation
        # Portfolio value = cash 500 + holdings 5*150=750 = 1250
        # Profit = 1250 - 1000 = 250
        self.assertEqual(self.account.calculate_profit_or_loss(), 250.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_loss(self, mock_get_price):
        """Test profit/loss with loss scenario."""
        # Simulate buying high, price decreases
        mock_get_price.return_value = 200.0  # Higher price for buying
        self.account.buy_shares('AAPL', 5)  # Cost 1000, balance 0
        mock_get_price.return_value = 150.0  # Price decreases for valuation
        # Portfolio value = cash 0 + holdings 5*150=750 = 750
        # Profit = 750 - 1000 = -250 (loss)
        self.assertEqual(self.account.calculate_profit_or_loss(), -250.0)

class TestAccountListMethods(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
    
    @patch('accounts.get_share_price')
    def test_list_holdings(self, mock_get_price):
        """Test list_holdings returns a copy."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 2)
        holdings = self.account.list_holdings()
        self.assertEqual(holdings, {'AAPL': 2})
        # Modify the copy, original should not change
        holdings['AAPL'] = 5
        self.assertEqual(self.account.holdings, {'AAPL': 2})
    
    @patch('accounts.get_share_price')
    def test_list_transactions(self, mock_get_price):
        """Test list_transactions returns a copy."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 2)
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 2)
        # Modify the copy, original should not change
        transactions.append({'test': 'data'})
        self.assertEqual(len(self.account.transactions), 2)

class TestAccountProfitOrLossAtTime(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account(1000.0)
        # Record initial timestamp
        self.initial_time = time.time()
        # Small delay to ensure different timestamps
        time.sleep(0.01)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_at_time_initial(self, mock_get_price):
        """Test profit/loss at initial time (should be zero)."""
        mock_get_price.return_value = 150.0
        profit_loss = self.account.calculate_profit_or_loss_at_time(self.initial_time)
        self.assertEqual(profit_loss, 0.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_at_time_after_buy(self, mock_get_price):
        """Test profit/loss at time after buying shares."""
        mock_get_price.return_value = 150.0
        # Buy shares at current time
        self.account.buy_shares('AAPL', 2)  # Cost 300
        buy_time = time.time()
        time.sleep(0.01)
        
        # Calculate profit/loss at buy time
        profit_loss = self.account.calculate_profit_or_loss_at_time(buy_time)
        # At buy time: cash 700, holdings 2*150=300, total 1000, initial 1000 => profit 0
        self.assertEqual(profit_loss, 0.0)
    
    @patch('accounts.get_share_price')
    def test_calculate_profit_or_loss_at_time_between_transactions(self, mock_get_price):
        """Test profit/loss at time between transactions."""
        mock_get_price.return_value = 150.0
        # First buy
        self.account.buy_shares('AAPL', 2)  # Cost 300
        time_between = time.time()
        time.sleep(0.01)
        # Second buy
        self.account.buy_shares('AAPL', 1)  # Cost 150
        
        # Calculate profit/loss at time between buys
        profit_loss = self.account.calculate_profit_or_loss_at_time(time_between)
        # At time_between: only first buy happened
        # Cash: 1000 - 300 = 700
        # Holdings: 2 * 150 = 300
        # Total: 1000, initial 1000 => profit 0
        self.assertEqual(profit_loss, 0.0)
    
    @patch('accounts.get_