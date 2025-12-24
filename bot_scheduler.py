#!/usr/bin/env python3
"""
🔥 WEST MONEY OS - AI BOT SCHEDULER 🔥
Hintergrund-Automatisierung für alle AI Bots

Bots:
- LeadScoringBot: Alle 30 Minuten
- FollowUpBot: Alle 60 Minuten  
- SyncBot: Alle 5 Minuten
- RecurringBillingBot: Täglich um 00:00
"""

import os
import sys
import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_bots.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('WestMoneyBots')

# Bot execution functions
def run_lead_scoring():
    """Run Lead Scoring Bot"""
    try:
        from app import app, LeadScoringBot
        with app.app_context():
            logger.info("🎯 Running LeadScoringBot...")
            result = LeadScoringBot.run()
            logger.info(f"✅ LeadScoringBot completed: {result}")
    except Exception as e:
        logger.error(f"❌ LeadScoringBot error: {e}")

def run_follow_up():
    """Run Follow-Up Bot"""
    try:
        from app import app, FollowUpBot
        with app.app_context():
            logger.info("📞 Running FollowUpBot...")
            result = FollowUpBot.run()
            logger.info(f"✅ FollowUpBot completed: {result}")
    except Exception as e:
        logger.error(f"❌ FollowUpBot error: {e}")

def run_sync():
    """Run Sync Bot (HubSpot)"""
    try:
        from app import app, SyncBot
        with app.app_context():
            logger.info("🔄 Running SyncBot...")
            result = SyncBot.run()
            logger.info(f"✅ SyncBot completed: {result}")
    except Exception as e:
        logger.error(f"❌ SyncBot error: {e}")

def run_recurring_billing():
    """Run Recurring Billing Check"""
    try:
        from app import app, RecurringBillingService
        with app.app_context():
            logger.info("💳 Running RecurringBillingService...")
            result = RecurringBillingService.process_due_subscriptions()
            logger.info(f"✅ RecurringBilling completed: {result}")
            
            # Also send renewal reminders
            reminder_result = RecurringBillingService.send_renewal_reminders()
            logger.info(f"✅ Renewal reminders sent: {reminder_result}")
    except Exception as e:
        logger.error(f"❌ RecurringBilling error: {e}")

def run_all_bots():
    """Run all bots immediately"""
    logger.info("🚀 Running ALL BOTS...")
    run_lead_scoring()
    run_follow_up()
    run_sync()
    logger.info("✅ All bots completed!")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler(
        timezone='Europe/Berlin',
        job_defaults={
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60
        }
    )
    
    # Add jobs
    scheduler.add_job(
        run_lead_scoring,
        IntervalTrigger(minutes=30),
        id='lead_scoring',
        name='Lead Scoring Bot',
        replace_existing=True
    )
    
    scheduler.add_job(
        run_follow_up,
        IntervalTrigger(minutes=60),
        id='follow_up',
        name='Follow-Up Bot',
        replace_existing=True
    )
    
    scheduler.add_job(
        run_sync,
        IntervalTrigger(minutes=5),
        id='sync',
        name='Sync Bot',
        replace_existing=True
    )
    
    scheduler.add_job(
        run_recurring_billing,
        CronTrigger(hour=0, minute=0),  # Daily at midnight
        id='recurring_billing',
        name='Recurring Billing',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("🤖 AI Bot Scheduler started!")
    logger.info("📋 Scheduled jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"   - {job.name}: {job.trigger}")
    
    return scheduler

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  🔥 WEST MONEY OS - AI BOT SCHEDULER 🔥                   ║
    ║  BROLY ULTRA GODMODE - Background Automation              ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Bots:                                                    ║
    ║  • LeadScoringBot    - Every 30 minutes                   ║
    ║  • FollowUpBot       - Every 60 minutes                   ║
    ║  • SyncBot           - Every 5 minutes                    ║
    ║  • RecurringBilling  - Daily at 00:00                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run all bots once on startup
    run_all_bots()
    
    # Start scheduler
    scheduler = start_scheduler()
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
