import logging

from . import model
from .client import client

log = logging.getLogger(__name__)


class Machine(model.ModelEntity):
    async def destroy(self, force=False):
        """Remove this machine from the model.

        Blocks until the machine is actually removed.

        """
        facade = client.ClientFacade.from_connection(self.connection)

        log.debug(
            'Destroying machine %s', self.id)

        await facade.DestroyMachines(force, [self.id])
        return await self.model._wait(
            'machine', self.id, 'remove')
    remove = destroy

    def run(self, command, timeout=None):
        """Run command on this machine.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        raise NotImplementedError()

    async def set_annotations(self, annotations):
        """Set annotations on this machine.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        log.debug('Updating annotations on machine %s', self.id)

        self.ann_facade = client.AnnotationsFacade.from_connection(
            self.connection)

        ann = client.EntityAnnotations(
            entity=self.id,
            annotations=annotations,
        )
        return await self.ann_facade.Set([ann])

    def scp(
            self, source_path, user=None, destination_path=None, proxy=False,
            scp_opts=None):
        """Transfer files to this machine.

        :param str source_path: Path of file(s) to transfer
        :param str user: Remote username
        :param str destination_path: Destination of transferred files on
            remote machine
        :param bool proxy: Proxy through the Juju API server
        :param str scp_opts: Additional options to the `scp` command

        """
        raise NotImplementedError()

    def ssh(
            self, command, user=None, proxy=False, ssh_opts=None):
        """Execute a command over SSH on this machine.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command

        """
        raise NotImplementedError()

    def status_history(self, num=20, utc=False):
        """Get status history for this machine.

        :param int num: Size of history backlog
        :param bool utc: Display time as UTC in RFC3339 format

        """
        raise NotImplementedError()
