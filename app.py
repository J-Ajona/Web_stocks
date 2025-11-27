from flask import Flask, render_template, jsonify
from tradingview_screener import Query, Column
import pandas as pd
import random
import copy

app = Flask(__name__)

# Global cache to store the initial "real" or "mock" data
# Global cache to store the initial "real" or "mock" data
BASE_DATA = {
    'spain': [],
    'usa': []
}

def fetch_initial_data():
    """
    Fetches initial data from TradingView using the tradingview-screener library.
    This runs once to set the baseline.
    """
    global BASE_DATA
    
    print("Fetching initial data from TradingView...")

    def get_specific_stocks(market, targets):
        try:
            # Fetch top 100 by market cap to ensure we find our blue chips
            q = Query().set_markets(market).select('name', 'close', 'change', 'volume', 'description', 'type', 'market_cap_basic')
            q = q.order_by('market_cap_basic', ascending=False).limit(100)
            
            count, df = q.get_scanner_data()
            
            if df is None or df.empty:
                return []
            
            stocks = []
            found_tickers = set()
            
            # First pass: find our targets
            for _, row in df.iterrows():
                symbol = row['ticker'].split(':')[-1] if ':' in row['ticker'] else row['ticker']
                
                # Check if this is one of our targets
                # We use a loose match or exact match? Tickers can be "SAN" or "SAN.MC" etc.
                # TradingView usually returns "SAN" for Santander in Spain market.
                # Let's normalize to upper case.
                if symbol.upper() in targets:
                    stocks.append({
                        'symbol': symbol,
                        'name': row['description'],
                        'price': float(row['close']),
                        'change': float(row['change']),
                        'color': 'green' if row['change'] >= 0 else 'red'
                    })
                    found_tickers.add(symbol.upper())
            
            # Sort stocks to match the order of targets list
            ordered_stocks = []
            for target in targets:
                for stock in stocks:
                    if stock['symbol'].upper() == target:
                        ordered_stocks.append(stock)
                        break
            
            return ordered_stocks
        except Exception as e:
            print(f"Error fetching data for {market}: {e}")
            return []

    # Fetch data for regions
    # USA: Nvidia, Microsoft, Apple
    usa_targets = ['NVDA', 'MSFT', 'AAPL']
    usa_stocks = get_specific_stocks('america', usa_targets)
    if usa_stocks:
        BASE_DATA['usa'] = usa_stocks
        
    # Spain: Iberdrola, Santander, Telefónica
    # Note: Tickers might be IBE, SAN, TEF
    spain_targets = ['IBE', 'SAN', 'TEF']
    spain_stocks = get_specific_stocks('spain', spain_targets)
    if spain_stocks:
        BASE_DATA['spain'] = spain_stocks

    print("Initial data fetch complete.")

# Initialize data on startup
fetch_initial_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    # Create a deep copy to avoid modifying the global BASE_DATA permanently
    # We want fluctuations to be around the base, or cumulative?
    # Let's make them cumulative for this session to look real, but we modify the response
    # Actually, to simulate live ticker, we should probably modify the base slightly or just return a variation.
    # Let's return a variation of the BASE_DATA so the "trend" stays similar but values dance.
    
    current_data = copy.deepcopy(BASE_DATA)
    
    for region in current_data:
        for stock in current_data[region]:
             # Fluctuate price by -0.5% to +0.5%
            fluctuation = random.uniform(-0.005, 0.005)
            stock['price'] = round(stock['price'] * (1 + fluctuation), 2)
            
            # Fluctuate change by -0.1% to +0.1%
            change_fluctuation = random.uniform(-0.1, 0.1)
            stock['change'] = round(stock['change'] + change_fluctuation, 2)
            
            # Format strings for display
            stock['price'] = f"{stock['price']:.2f}"
            stock['change'] = f"{'+' if stock['change'] > 0 else ''}{stock['change']:.1f}%"
            stock['color'] = 'green' if float(stock['change'].strip('%')) >= 0 else 'red'

    return jsonify(current_data)

if __name__ == '__main__':
    app.run(debug=True)
