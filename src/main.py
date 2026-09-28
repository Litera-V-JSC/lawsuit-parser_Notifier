import asyncio
import sys

from src.subscribers import load_subscribers
from src.api_client.parser_client import ParserClient
from src.email_sender.smtp_sender import SmtpSender
from src.scheduler.scheduler import SubscriberScheduler
from src.utils.logger import setup_logger


async def main():
    logger = setup_logger()
    logger.info('Starting email notifier...')

    try:
        data = load_subscribers()
    except Exception as e:
        logger.error(f'Failed to load subscribers: {e}')
        return 1

    subscribers = data['subscribers']
    smtp_config = data['smtp']
    logger.info(f'Loaded {len(subscribers)} subscribers from {data["source"]}')

    parser = ParserClient()
    try:
        health = await parser.health()
        logger.info(f'Parser API health: {health}')
    except Exception as e:
        logger.error(f'Cannot reach parser API: {e}')
        await parser.close()
        return 1

    sender = SmtpSender(smtp_config)

    scheduler = SubscriberScheduler(parser, sender, subscribers)
    scheduler.start()
    logger.info('Scheduler started')

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info('Shutting down')
    finally:
        scheduler.shutdown()
        await parser.close()

    return 0


if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(0)
