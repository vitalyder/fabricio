import json

import mock
import unittest2 as unittest

from fabric import api as fab

import fabricio

from fabricio.apps.python.django import DjangoContainer, DjangoService, DjangoStack
from fabricio.docker.service import FailoverService
from tests import SucceededResult, docker_run_args_parser, args_parser, \
    docker_inspect_args_parser


class DjangoContainerTestCase(unittest.TestCase):

    @mock.patch.object(FailoverService, 'is_manager', return_value=True)
    def test_migrate(self, *args):
        cases = dict(
            container_default=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoContainer,
            ),
            service_default=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoService,
            ),
            stack_default=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoStack,
            ),
            container_with_tag_and_registry_and_account=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'registry/account/image:foo',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(tag='foo', registry='registry', account='account'),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoContainer,
            ),
            service_with_tag_and_registry_and_account=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'registry/account/image:foo',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(tag='foo', registry='registry', account='account'),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoService,
            ),
            stack_with_tag_and_registry_and_account=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'registry/account/image:foo',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(tag='foo', registry='registry', account='account'),
                service_init_kwargs=dict(name='name', image='image:tag'),
                service_type=DjangoStack,
            ),
            customized_container=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'user': 'user',
                    'env': ['env'],
                    'volume': ['volumes'],
                    'link': ['links'],
                    'label': ['label'],
                    'add-host': ['hosts'],
                    'net': 'network',
                    'stop-signal': 'stop_signal',
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(
                    name='name',
                    image='image:tag',
                    stop_timeout='stop_timeout',
                    command='command',

                    options=dict(
                        user='user',
                        env='env',
                        volume='volumes',
                        link='links',
                        add_host='hosts',
                        network='network',
                        stop_signal='stop_signal',
                        label='label',

                        publish='ports',
                        restart='restart_policy',
                    ),
                ),
                service_type=DjangoContainer,
            ),
            customized_service=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'user': 'user',
                    'env': ['env'],
                    'label': ['container_labels'],
                    'add-host': ['foo:127.0.0.1'],
                    'network': 'network',
                    'rm': True,
                    'tty': True,
                    'interactive': True,
                    'mount': 'mounts',
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(
                    name='name',
                    image='image:tag',
                    command='command',
                    args='args',
                    mode='mode',

                    options=dict(
                        user='user',
                        env='env',
                        network='network',
                        container_label='container_labels',
                        host='foo:127.0.0.1',

                        secret='secret',
                        label='label',
                        stop_grace_period='stop_timeout',
                        restart_condition='restart_condition',
                        publish='ports',
                        mount='mounts',
                        replicas='replicas',
                        constraint='constraints',
                    ),
                ),
                service_type=DjangoService,
            ),
            customized_stack=dict(
                expected_args={
                    'executable': ['docker'],
                    'run_or_create': ['run'],
                    'rm': True,
                    'tty': True,
                    'custom-option': 'custom-option',
                    'interactive': True,
                    'image': 'image:tag',
                    'command': ['python', 'manage.py', 'migrate', '--noinput'],
                },
                kwargs=dict(),
                service_init_kwargs=dict(
                    name='name',
                    image='image:tag',
                    safe_options={'custom-option': 'custom-option'},
                ),
                service_type=DjangoStack,
            ),
        )

        def test_command(command, *args, **kwargs):
            options = docker_run_args_parser.parse_args(command.split())
            self.assertDictEqual(vars(options), data['expected_args'])
        for case, data in cases.items():
            with self.subTest(case=case):
                fab.env.command = '{0}__{1}'.format(self, case)
                with mock.patch.object(fabricio, 'run', side_effect=test_command) as run:
                    service = data['service_type'](**data['service_init_kwargs'])
                    with fab.settings(fab.hide('everything')):
                        service.migrate(**data['kwargs'])
                        run.assert_called_once()

    @mock.patch.object(FailoverService, 'is_manager', return_value=True)
    def test_migrate_back(self, *args):
        cases = dict(
            container_no_change=dict(
                side_effect=(
                    SucceededResult('[{"Image": "current_image_id"}]'),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult('[{"Image": "backup_image_id"}]'),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'inspect', '--type', 'container', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    dict(args=['docker', 'inspect', '--type', 'container', 'name_backup']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoContainer,
            ),
            service_no_change=dict(
                side_effect=(
                    SucceededResult(json.dumps([{
                        "Spec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@digest"}}},
                        "PreviousSpec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@backup"}}},
                    }])),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'service', 'inspect', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoService,
            ),
            stack_no_change=dict(
                side_effect=(
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                ),
                args_parsers=[
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoStack,
            ),
            service_double_revert=dict(
                side_effect=(
                    SucceededResult(json.dumps([{
                        "Spec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@backup"}}},
                        "PreviousSpec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@digest"}}},
                    }])),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app4.0001_initial\n'
                        'app4.0001_foo\n'
                    ),
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'service', 'inspect', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app4', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoService,
            ),
            container_no_migrations=dict(
                side_effect=(
                    SucceededResult('[{"Image": "current_image_id"}]'),
                    SucceededResult(),
                    SucceededResult('[{"Image": "backup_image_id"}]'),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'inspect', '--type', 'container', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    dict(args=['docker', 'inspect', '--type', 'container', 'name_backup']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoContainer,
            ),
            service_no_migrations=dict(
                side_effect=(
                    SucceededResult(json.dumps([{
                        "Spec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@digest"}}},
                        "PreviousSpec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@backup"}}},
                    }])),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'service', 'inspect', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoService,
            ),
            stack_no_migrations=dict(
                side_effect=(
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoStack,
            ),
            container_regular=dict(
                side_effect=(
                    SucceededResult('[{"Image": "current_image_id"}]'),
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n\n'
                    ),
                    SucceededResult('[{"Image": "backup_image_id"}]'),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app4.0001_initial\n'
                        'app4.0001_foo\n\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'inspect', '--type', 'container', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    dict(args=['docker', 'inspect', '--type', 'container', 'name_backup']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoContainer,
            ),
            service_regular=dict(
                side_effect=(
                    SucceededResult(json.dumps([{
                        "Spec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@digest"}}},
                        "PreviousSpec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@backup"}}},
                    }])),
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    dict(args=['docker', 'service', 'inspect', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoService,
            ),
            stack_regular=dict(
                side_effect=(
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                args_parsers=[
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                expected_args=[
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                service_type=DjangoStack,
            ),
            container_custom_options=dict(
                side_effect=(
                    SucceededResult('[{"Image": "current_image_id"}]'),
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult('[{"Image": "backup_image_id"}]'),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                expected_args=[
                    dict(args=['docker', 'inspect', '--type', 'container', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    dict(args=['docker', 'inspect', '--type', 'container', 'name_backup']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'volume': ['volumes'],
                        'link': ['links'],
                        'add-host': ['hosts'],
                        'net': 'network',
                        'stop-signal': 'stop_signal',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'backup_image_id',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                init_kwargs=dict(
                    options=dict(
                        user='user',
                        env='env',
                        volume='volumes',
                        link='links',
                        add_host='hosts',
                        network='network',
                        stop_signal='stop_signal',

                        publish='ports',
                        restart='restart_policy',
                        custom='custom',
                    ),
                    command='command',
                    stop_timeout='stop_timeout',
                ),
                service_type=DjangoContainer,
            ),
            service_custom_options=dict(
                side_effect=(
                    SucceededResult(json.dumps([{
                        "Spec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@digest"}}},
                        "PreviousSpec": {"TaskTemplate": {"ContainerSpec": {"Image": "image@backup"}}},
                    }])),
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                expected_args=[
                    dict(args=['docker', 'service', 'inspect', 'name']),
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@digest',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'user': 'user',
                        'env': ['env'],
                        'label': ['container_labels'],
                        'add-host': ['foo:127.0.0.1'],
                        'network': 'network',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'mount': 'mounts',
                        'image': 'image@backup',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                args_parsers=[
                    args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                init_kwargs=dict(
                    command='command',
                    args='args',
                    mode='mode',

                    options=dict(
                        user='user',
                        env='env',
                        network='network',
                        container_label='container_labels',
                        host='foo:127.0.0.1',

                        secret='secret',
                        label='label',
                        stop_grace_period='stop_timeout',
                        restart_condition='restart_condition',
                        publish='ports',
                        mount='mounts',
                        replicas='replicas',
                        constraint='constraints',
                        custom='custom',
                    ),
                ),
                service_type=DjangoService,
            ),
            stack_custom_options=dict(
                side_effect=(
                    SucceededResult(
                        'app0.0001_initial\n'
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                        'app3.0001_initial\n'
                        'app2.0002_foo\n'
                        'app3.0002_foo\n'
                    ),
                    SucceededResult(
                        'app1.0001_initial\n'
                        'app1.0002_foo\n'
                        'app2.0001_initial\n'
                    ),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                    SucceededResult(),
                ),
                expected_args=[
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app3', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app2', '0001_initial'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'image:tag',
                        'command': ['python', 'manage.py', 'migrate', '--no-input', 'app0', 'zero'],
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'custom-option': 'custom-option',
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'fabricio-backup-stack:name',
                        'command': ['python', 'manage.py', 'migrate', '--noinput'],
                    },
                ],
                args_parsers=[
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                    docker_run_args_parser,
                ],
                init_kwargs=dict(
                    safe_options={
                        'custom-option': 'custom-option',
                    },
                ),
                service_type=DjangoStack,
            ),
        )

        def test_command(command, *args, **kwargs):
            parser = next(args_parsers)
            options = parser.parse_args(command.split())
            self.assertDictEqual(vars(options), next(expected_args))
            return next(side_effect)
        for case, data in cases.items():
            expected_args = iter(data['expected_args'])
            args_parsers = iter(data['args_parsers'])
            side_effect = iter(data['side_effect'])
            with self.subTest(case=case):
                fab.env.command = '{0}__{1}'.format(self, case)
                with mock.patch.object(
                    fabricio,
                    'run',
                    side_effect=test_command,
                ) as run:
                    service = data['service_type'](
                        name='name',
                        image='image:tag',
                        **data.get('init_kwargs', {})
                    )
                    service.migrate_back()
                    self.assertEqual(run.call_count, len(data['side_effect']))

    maxDiff = None

    def test_migrate_back_errors(self):
        cases = dict(
            current_container_not_found=dict(
                expected_exception=RuntimeError,
                side_effect=(
                    RuntimeError(),
                ),
                args_parsers=[
                    docker_inspect_args_parser,
                ],
                expected_args=[
                    {
                        'executable': ['docker', 'inspect'],
                        'type': 'container',
                        'image_or_container': 'name',
                    },
                ],
            ),
            backup_container_not_found=dict(
                expected_exception=RuntimeError,
                side_effect=(
                    SucceededResult('[{"Image": "current_image_id"}]'),
                    SucceededResult(
                        'app1.0001_initial\n'
                    ),
                    RuntimeError(),
                ),
                args_parsers=[
                    docker_inspect_args_parser,
                    docker_run_args_parser,
                    docker_inspect_args_parser,
                ],
                expected_args=[
                    {
                        'executable': ['docker', 'inspect'],
                        'type': 'container',
                        'image_or_container': 'name',
                    },
                    {
                        'executable': ['docker'],
                        'run_or_create': ['run'],
                        'rm': True,
                        'tty': True,
                        'interactive': True,
                        'image': 'current_image_id',
                        'command': ['python', 'manage.py', 'showmigrations', '--plan', '|', 'egrep', "'^\\[X\\]'", '|', 'awk', "'{print", "$2}'", '&&', 'test', '${PIPESTATUS[0]}', '-eq', '0'],
                    },
                    {
                        'executable': ['docker', 'inspect'],
                        'type': 'container',
                        'image_or_container': 'name_backup',
                    },
                ],
            ),
        )

        def test_command(command, *args, **kwargs):
            parser = next(args_parsers)
            options = parser.parse_args(command.split())
            self.assertDictEqual(vars(options), next(expected_args))
            result = next(side_effect)
            if isinstance(result, Exception):
                raise result
            return result
        for case, data in cases.items():
            fab.env.command = '{0}__{1}'.format(self, case)
            expected_args = iter(data['expected_args'])
            args_parsers = iter(data['args_parsers'])
            side_effect = iter(data['side_effect'])
            with self.subTest(case=case):
                with mock.patch.object(fabricio, 'run', side_effect=test_command):
                    container = DjangoContainer(name='name', image='image')
                    with self.assertRaises(data['expected_exception']):
                        container.migrate_back()
