import argparse
from datetime import datetime
from dotenv import load_dotenv
from tools.alpaca_api import place_order, get_account, get_positions
from main import run_hedge_fund
from colorama import Fore, Style, init

# Load environment variables
load_dotenv()
init(autoreset=True)

def execute_trades():
    """Execute paper trades based on hedge fund recommendations."""
    parser = argparse.ArgumentParser(description='AI Hedge Fund Paper Trading')
    parser.add_argument('--ticker', type=str, required=True, help='Comma-separated list of tickers')
    parser.add_argument('--show-reasoning', action='store_true', help='Show agent reasoning')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # Run the hedge fund to get recommendations
    tickers = args.ticker.split(',')
    
    # Set the start and end dates
    end_date = args.end_date or datetime.now().strftime("%Y-%m-%d")
    if not args.start_date:
        # Calculate 3 months before end_date
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (end_date_obj - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    else:
        start_date = args.start_date
    
    # Run the hedge fund
    results = run_hedge_fund(
        tickers=tickers,
        show_reasoning=args.show_reasoning,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get account information
    account = get_account()
    print(f"\n{Fore.CYAN}Account Information:{Style.RESET_ALL}")
    print(f"Cash: ${float(account.cash):.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):.2f}")
    
    # Execute trades based on recommendations
    print(f"\n{Fore.GREEN}Executing Trades:{Style.RESET_ALL}")
    for ticker, decision in results.items():
        action = decision.get('action', 'hold').lower()
        quantity = decision.get('quantity', 0)
        
        if action in ['buy', 'sell'] and quantity > 0:
            try:
                side = 'buy' if action == 'buy' else 'sell'
                order = place_order(ticker, quantity, side)
                print(f"{Fore.GREEN}Order placed: {side.upper()} {quantity} shares of {ticker}{Style.RESET_ALL}")
                print(f"Order ID: {order.id}")
                print(f"Order Status: {order.status}")
            except Exception as e:
                print(f"{Fore.RED}Error placing order for {ticker}: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No action taken for {ticker}{Style.RESET_ALL}")
    
    # Show current positions
    positions = get_positions()
    if positions:
        print(f"\n{Fore.CYAN}Current Positions:{Style.RESET_ALL}")
        for position in positions:
            print(f"{position.symbol}: {position.qty} shares, Current Value: ${float(position.market_value):.2f}")

if __name__ == "__main__":
    execute_trades()