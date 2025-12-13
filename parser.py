import sqlite3
import pandas as pd
from datetime import datetime

def parse_sms(db_path):
    """
    Parse SMS/MMS database and extract messages.
    
    Args:
        db_path: Path to mmssms.db file
        
    Returns:
        DataFrame with SMS data including address, date, body, type
    """
    try:
        conn = sqlite3.connect(db_path)
        # Detailed query to join sender address and body
        query = "SELECT address, date, body, type FROM sms"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Convert timestamp (Android typically uses ms)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        
        # Map message types (1=Inbox, 2=Sent)
        df['type'] = df['type'].map({1: 'Incoming', 2: 'Outgoing'})
        
        df['artifact_type'] = 'SMS'
        return df
    except Exception as e:
        print(f"Error parsing SMS: {e}")
        return pd.DataFrame()

def parse_call_logs(db_path):
    """
    Parse call log database and extract call records.
    
    Args:
        db_path: Path to calllog.db file
        
    Returns:
        DataFrame with call data including number, date, duration, type
    """
    try:
        conn = sqlite3.connect(db_path)
        # Query for calls
        query = "SELECT number, date, duration, type FROM calls"
        df = pd.read_sql_query(query, conn)
        conn.close()

        df['date'] = pd.to_datetime(df['date'], unit='ms')
        
        # Map call types (1=Incoming, 2=Outgoing, 3=Missed)
        df['type'] = df['type'].map({1: 'Incoming', 2: 'Outgoing', 3: 'Missed'})
        
        df['artifact_type'] = 'Call Log'
        return df
    except Exception as e:
        print(f"Error parsing Call Logs: {e}")
        return pd.DataFrame()

def parse_chrome_history(db_path):
    """
    Parse Chrome browser history database.
    
    Args:
        db_path: Path to Chrome History file
        
    Returns:
        DataFrame with browser history including date, url, title
    """
    try:
        conn = sqlite3.connect(db_path)
        # Chrome uses Webkit timestamp format (microseconds since 1601)
        # We simplify strictly for example purposes
        query = "SELECT url, title, last_visit_time FROM urls"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Timestamp conversion is complex for Chrome; this is a simplified approximation
        # (visit_time / 1000000) - 11644473600 gives unix timestamp
        df['date'] = pd.to_datetime((df['last_visit_time']/1000000)-11644473600, unit='s', errors='coerce')
        
        df['artifact_type'] = 'Browser History'
        return df[['date', 'url', 'title', 'artifact_type']]
    except Exception as e:
        print(f"Error parsing Chrome: {e}")
        return pd.DataFrame()

