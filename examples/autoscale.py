#!/usr/bin/env python3.5

"""
Juju auto-scaler.


Example config:

    ubuntu:
        min-units: 1
        max-units: 5
        deploy:
            charm: ubuntu
            series: xenial
            channel: stable
        alarms:
            add-capacity-alarm:
                statistic: average
                metric: cpu
                comparator: >=
                threshold: 80
                period: 300
                policies:
                    add-capacity:
                        scaling-adjustment: 30
                        adjustment-type: percent
                        warmup: 300
            decrease-capacity-alarm:
                statistic: average
                metric: cpu
                comparator: <=
                threshold: 40
                period: 300
                policies:
                    decrease-capacity:
                        when: decrease-capacity-alarm
                        scaling-adjustment: 1
                        adjustment-type: units

"""

import argparse
import asyncio
import logging
import signal
import textwrap

from juju.model import Model


def setup_parser():
    """Setup parser for cmdline args.

    """
    parser = argparse.ArgumentParser(
        prog='autoscale',
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-l', '--log-level',
        choices=('INFO', 'DEBUG', 'WARN', 'ERROR', 'CRITICAL'),
        default='INFO',
    )

    return parser


class Alarm:
    """Monitors an application and executes scaling policies if an alarm
    condition is met.

    """
    def __init__(self, name, config, app_name, model, loop=None):
        self.name = name
        self.config = config
        self.app_name = app_name
        self.model = model
        self.loop = loop or asyncio.get_event_loop()

    def enable(self):
        """Start monitoring for the alarm condition.

        """
        app = model


class AutoScaler:
    """Auto-scales a single Juju application in a single model.

    """
    def __init__(self, app_name, config, model, loop=None):
        """Initialize the AutoScaler.

        :param app_name: The Juju application name
        :param config: Dictionary of auto-scaling rules
        :param model: The :class:`juju.model.Model` in which to operate
        :param loop: An asyncio-compatible event loop

        """
        self.app_name = app_name
        self.config = config
        self.model = model
        self.loop = loop or asyncio.get_event_loop()

    async def start(self):
        """Start the AutoScaler.

        Initiates a loop which monitors the status of the application and
        applies auto-scaling rules as appropriate.

        Under normal circumstances this will run forever, or until stopped.

        """
        while True:
            await asyncio.sleep(self.check_interval())

            app = self.model.applications.get(self.app_name)

            # App deployed?
            if not app:
                await self.deploy()
                continue

            # Too many units?
            if len(app.units) > self.max_units():
                await self.destroy_units(
                    app, len(app.units) - self.max_units()
                )
                continue

            # Too few units?
            if len(app.units) < self.min_units():
                await self.add_units(
                    app, self.min_units() - len(app.units)
                )
                continue

    async def deploy(self):
        """Deploy the application.

        Called when the AutoScaler is run against a model in which the
        application is not yet deployed.

        Requires that the AutoScaler config includes a 'deploy' block,
        otherwise an Exception will be raised.

        :return: :class:`juju.application.Application` instance

        """
        if 'deploy' not in self.config:
            raise Exception(
                "%s can not be auto-deployed due to missing"
                "'deploy' block in config." % self.app_name
            )

        deploy_cfg = self.config['deploy']
        charm = deploy_cfg.pop('charm', self.app_name)
        deploy_cfg.pop('application_name', None)

        logging.info('Deploying %s', self.app_name)

        return await self.model.deploy(
            charm,
            application_name=self.app_name,
            **deploy_cfg,
        )

    async def destroy_units(self, app, num_units):
        """Destroy one or more units of the application.

        :param app: :class:`juju.application.Application`
        :param num_units: Number of units to destroy

        """
        def cmp(name):
            return int(name.split('/')[-1])

        unit_names = [u.name for u in app.units]
        unit_names = sorted(unit_names, key=cmp, reverse=True)

        return await self.model.destroy_units(unit_names[:num_units])

    async def add_units(self, app, num_units):
        """Add one or more units of the application.

        :param app: :class:`juju.application.Application`
        :param num_units: Number of units to add

        """
        return await app.add_units(count=num_units)


async def run(loop, args):
    model = Model(loop)
    await model.connect_current()

    await model.disconnect()


def main():
    parser = setup_parser()
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=getattr(logging, args.log_level),
    )
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), loop.stop)

    try:
        loop.run_until_complete(run(loop, args))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
