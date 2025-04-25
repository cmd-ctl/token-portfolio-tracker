# Crypto Portfolio Tracker - Documentation

## Overview
This Python script provides a comprehensive solution for tracking cryptocurrency portfolios by:
- Fetching real-time prices from CoinMarketCap API
- Calculating portfolio value and price changes
- Storing historical data in SQLite database
- Displaying formatted portfolio updates in console
- Running automatically with 5-minute updates

## Requirements
- Python 3.8+
- Required packages:
  - `requests`
  - `python-dotenv`
  - `sqlite3` (built-in)

## Installation
1. Clone the repository or download the script
2. Install dependencies:
```bash
pip install requests python-dotenv
```
3. Set up your environment variables and configuration

## Configuration

### Environment Variables
Create a `.env` file with your CoinMarketCap API key:
```env
CMC_API_KEY=your_api_key_here
```

### Config File
Create a `config.json` file with your portfolio and preferred currency:
```json
{
  "portfolio": {
    "BTC": 0.5,
    "ETH": 3.2,
    "SOL": 25.0
  },
  "currency": "USD"
}
```

## Database Structure
The script creates and maintains an SQLite database (`portfolio.db`) with two tables:

### `tokens` Table
Stores individual token data for each update:
- `id`: Auto-incrementing primary key
- `timestamp`: Date and time of update
- `symbol`: Token symbol (e.g., BTC)
- `amount`: Amount held
- `price`: Current price
- `value`: Current value (amount × price)
- `price_change`: Percentage change from previous price

### `portfolio_history` Table
Stores portfolio summary for each update:
- `id`: Auto-incrementing primary key
- `timestamp`: Date and time of update
- `total_value`: Total portfolio value
- `currency`: Display currency
- `value_change`: Percentage change from previous total value

## Functions

### `init_db()`
Initializes the SQLite database with required tables.

### `load_config()`
Loads portfolio configuration from `config.json`.

### `get_cmc_data(api_key, symbols, currency)`
Fetches latest prices from CoinMarketCap API.

### `get_previous()`
Retrieves previous total portfolio value from database.

### `get_previous_prices(symbol)`
Retrieves previous price for a specific token.

### `save_to_db(tokens_data, total_value, currency, value_change)`
Saves current portfolio data to database.

### `display_portfolio(data, total, currency, total_change)`
Displays formatted portfolio information in console.

### `main()`
Main execution loop that runs every 5 minutes.

## Usage
Simply run the script:
```bash
python portfolio_tracker.py
```

The script will:
1. Initialize the database (if not exists)
2. Load your portfolio configuration
3. Fetch current prices from CoinMarketCap
4. Calculate values and changes
5. Store data in the database
6. Display formatted output
7. Repeat every 5 minutes

## Output Example
```
----------------------------------------------------------------------
2023-12-15 14:30:00 | Update
----------------------------------------------------------------------
BTC: 0.5  | Price: 42500.00 USD | Value: 21250.00 USD | Change: +1.25%
ETH: 3.2  | Price: 2250.50 USD | Value: 7201.60 USD | Change: -0.75%
SOL: 25.0 | Price: 102.75 USD | Value: 2568.75 USD | Change: +3.20%
----------------------------------------------------------------------
TOTAL: 31020.35 USD (+0.85%)
```


