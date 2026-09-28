from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.api_client.parser_client import ParserClient, ParserApiError
from src.formatting import formatter
from src.utils.logger import setup_logger


logger = setup_logger()


class SubscriberScheduler:
    def __init__(self, parser: ParserClient, sender, subscribers: list):
        self.parser = parser
        self.sender = sender
        self.subscribers = subscribers
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()
        for idx, sub in enumerate(self.subscribers):
            self._schedule(sub, idx)

    def shutdown(self):
        try:
            self.scheduler.shutdown(wait=False)
        except Exception:
            pass

    def _interval_for(self, schedule: str) -> dict:
        if schedule == 'every_1_min':
            return {'minutes': 1}
        if schedule == 'every_2_min':
            return {'minutes': 2}
        if schedule == 'hourly':
            return {'hours': 1}
        if schedule == 'daily':
            return {'hours': 24}
        if schedule == 'monthly':
            return {'days': 30}
        return {'days': 7}

    def _schedule(self, subscriber, idx):
        email = subscriber.get('email', 'unknown')
        schedule = subscriber.get('schedule', 'weekly')
        interval = self._interval_for(schedule)

        self.scheduler.add_job(
            self._check_subscriber,
            trigger=IntervalTrigger(**interval),
            args=[subscriber],
            id=f'sub_{idx}_{email}',
            replace_existing=True,
        )
        logger.info(f'Scheduled {email} with interval {interval}')

    async def _check_subscriber(self, subscriber):
        email = subscriber.get('email')
        if not email:
            logger.warning('Subscriber without email, skipping')
            return

        watches = subscriber.get('watches', [])
        notify_on_no_change = bool(subscriber.get('notify_on_no_change', False))

        logger.info(f'Checking {len(watches)} watches for {email}')

        for inn in watches:
            try:
                await self.parser.parse_inn(inn)
                diff = await self.parser.get_diff_latest(inn)
            except ParserApiError as e:
                logger.error(f'Parser API error for {inn}: {e.code} - {e.message}')
                continue
            except Exception:
                logger.exception(f'Unexpected error checking {inn}')
                continue

            company_name = None
            try:
                latest = await self.parser.get_latest(inn)
                for source_data in latest.get('sources', {}).values():
                    if isinstance(source_data, dict):
                        company_name = (
                            source_data.get('company_name')
                            or source_data.get('short_name')
                        )
                        if company_name:
                            break
            except Exception:
                pass

            changed = bool(diff.get('changed'))
            if not changed and not notify_on_no_change:
                logger.info(f'No changes for {inn}, skipping email to {email}')
                continue

            if changed:
                subject = f'Изменения по ИНН {inn}'
                if company_name:
                    subject = f'Изменения: {company_name} (ИНН {inn})'
                body = formatter.format_diff_message(inn, diff, company_name)
            else:
                subject = f'Без изменений: {company_name or inn} (ИНН {inn})'
                body = formatter.format_no_change_message(inn, company_name)

            try:
                self.sender.send(email, subject, body)
                logger.info(f'Email sent to {email} for INN {inn} (changed={changed})')
            except Exception:
                logger.exception(f'Failed to send email to {email} for INN {inn}')
