#!/usr/bin/env python3
# Get Telegram Chat ID Helper

import requests
import json

def get_chat_id():
    """Get chat ID for your Telegram channel/group"""
    bot_token = "8366393794:AAH0ZKkoIzvDtBVfJa7woObbXaezhC_JBmU"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print("🔍 Checking for Telegram updates...")
    print(f"URL: {url}")
    
    try:
        print("📡 Making request to Telegram API...")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print("� Response received!")
        print(f"OK Status: {data.get('ok')}")
        
        if data.get('ok') and data.get('result'):
            print(f"📨 Found {len(data['result'])} updates")
            
            for i, update in enumerate(data['result']):
                print(f"\n--- Update {i+1} ---")
                if 'message' in update:
                    msg = update['message']
                    chat = msg['chat']
                    
                    print(f"📱 Chat Type: {chat['type']}")
                    print(f"🆔 Chat ID: {chat['id']}")
                    print(f"📝 Title: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                    print(f"💬 Message: {msg.get('text', 'No text')}")
                    
                    # This is what we need!
                    chat_id = chat['id']
                    print(f"\n🎯 YOUR CHAT ID: {chat_id}")
                    print(f"🔧 Add this to .env file:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
                    
        else:
            print("❌ No updates found. Please:")
            print("1. Make sure bot is added to your channel/group as admin")
            print("2. Send a test message in the channel mentioning @JobsFinderr_bot")
            print("3. Run this script again")
            print(f"4. Raw response: {data}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    get_chat_id()
