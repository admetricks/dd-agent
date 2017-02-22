# 3p
from nose.plugins.attrib import attr

# project
from tests.checks.common import AgentCheckTest
from utils.shell import which

COMMON_METRICS = [
    'squid3.syscalls.disk.unlinks',
]

@attr(requires='squid3')
class VarnishCheckTest(AgentCheckTest):
    CHECK_NAME = 'squid3'

    def test_check(self):
        squidclient_path = which('squidclient')
        self.assertTrue(squidclient_path is not None, "Flavored testing should be run with a real varnish")

        config = {
            'instances': [{
                'squidclient': squidclient_path,
                'tags': ['cluster:webs']
            }]
        }

        self.run_check(config)
        version = self.check._get_version_info(squidclient_path)

        self.assertTrue(version == 3)

        to_check = COMMON_METRICS

        for mname in to_check:
            self.assertMetric(mname, count=1, tags=['cluster:webs', 'squid3_name:default'])

        self.coverage_report()
