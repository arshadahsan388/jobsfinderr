import requests
import json

def find_chat_id():
    bot_token = "8366393794:AAH0ZKkoIzvDtBVfJa7woObbXaezhC_JBmU"
    
    # Method 1: Try to send to a common chat ID format
    test_chat_ids = [
        "@jobsfinderr_alerts",  # Channel username
        "@JobsFinderr_alerts",  # Channel username with capital
        "YOUR_PERSONAL_CHAT_ID"  # Will fail but show error message
    ]
    
    for chat_id in test_chat_ids:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': '🧪 TEST: Bot is working! Chat ID found!',
                'parse_mode': 'Markdown'
            }
            
            print(f"Testing Chat ID: {chat_id}")
            response = requests.post(url, data=payload)
            result = response.json()
            
            if result.get('ok'):
                print(f"✅ SUCCESS! Chat ID: {chat_id}")
                print(f"Message sent successfully!")
                return chat_id
            else:
                print(f"❌ Failed: {result.get('description', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error with {chat_id}: {e}")
    
    print("\n💡 To find your Chat ID:")
    print("1. Send /start to @JobsFinderr_bot in private chat")
    print("2. Or create public channel with username like @jobsfinderr_alerts")
    print("3. Add bot as admin with post permission")
    
if __name__ == "__main__":
    find_chat_id()
