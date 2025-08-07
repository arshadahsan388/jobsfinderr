#!/usr/bin/env python3
# Live Test for Telegram Bot

import os
import sys

# Set environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = '8366393794:AAH0ZKkoIzvDtBVfJa7woObbXaezhC_JBmU'
os.environ['TELEGRAM_CHAT_ID'] = '-4847462383'

print('🧪 TELEGRAM BOT LIVE TEST')
print('=' * 50)
print(f'Bot Token: {os.environ.get("TELEGRAM_BOT_TOKEN")[:20]}...')
print(f'Chat ID: {os.environ.get("TELEGRAM_CHAT_ID")}')
print()

try:
    from telegram_bot import send_telegram_job_notification
    
    # Sample job for testing
    sample_job = {
        'id': 'test_123',
        'title': 'TEST: Health Department Balochistan Jobs 2025',
        'details': {
            'Job Type': 'Government',
            'Location': 'Balochistan, Quetta',
            'Total Vacancies': '103',
            'Education': 'Graduation, Master Degree',
            'Salary': 'PKR 40000 – 150000',
            'Last Date for Apply': '06 August 2025'
        }
    }
    
    print('📤 Sending test message to Telegram group...')
    print('📱 Group: "JobsFinderr Alert"')
    print()
    
    result = send_telegram_job_notification(sample_job)
    
    print()
    if result:
        print('✅ SUCCESS! Message sent to Telegram group!')
        print('📱 Check your "JobsFinderr Alert" group')
        print('🔗 Message includes WhatsApp share link')
        print('🎉 Telegram automation is working!')
    else:
        print('❌ FAILED! Check the error messages above')
        print('🔧 Bot token and Chat ID are correct, check network')
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 50)
print('🎯 Test completed! Check your Telegram group!')
