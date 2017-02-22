# (C) Admetricks SpA, Inc. 2017
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# stdlib
from collections import defaultdict
import re
import xml.parsers.expat # python 2.4 compatible

# project
from checks import AgentCheck
from utils.subprocess_output import get_subprocess_output

class Squid3(AgentCheck):
    def check(self, instance):
        # Not configured? Not a problem.
        if instance.get("squidclient", None) is None:
            raise Exception("squidclient is not configured")
        tags = instance.get('tags', [])
        if tags is None:
            tags = []
        else:
            tags = list(set(tags))

        squidclient_path = instance.get("squidclient")
        name = instance.get('name')

        # Parse metrics from squidclient.
        cmd = [squidclient_path]
        cmd.extend(['-p', '3128', 'mgr:5min'])

        if name is not None:
            tags += [u'squid3_name:%s' % name]
        else:
            tags += [u'squid3_name:default']

        output, _, _ = get_subprocess_output(cmd, self.log)

        self._parse_squidclient(output, tags)

    def _parse_squidclient(self, output, tags=None):
        for line in output.splitlines():
            try:
                name, value = line.split(" = ")
            except:
                continue
            length = value.find('/')
            if length < 0:
                length = value.find(' ')
            if length < 0:
                length = value.find('%')
            if length < 0:
                length = None
            metric_name = self.normalize(name, prefix="squid3")
            self.log.debug("Squid3 %s %d" % (metric_name, float(value[0:length])))
            self.gauge(metric_name, float(value[0:length]), tags=tags)


    def _get_version_info(self, squidclient_path):
        # Get the squid version from squidclient
        output, error, _ = get_subprocess_output([squidclient_path, "--help"], self.log,
            raise_on_empty_output=False)

        # Assumptions regarding squid's version
        version = -1

        m1 = re.search(r"Version: (\d+)", output, re.MULTILINE)
        # v2 prints the version on stderr, v3 on stdout
        m2 = re.search(r"Version: (\d+)", error, re.MULTILINE)

        if m1 is None and m2 is None:
            self.log.warn("Cannot determine the version of squid")
            self.warning("Cannot determine the version of squid")
        else:
            if m1 is not None:
                version = int(m1.group(1))
            elif m2 is not None:
                version = int(m2.group(1))

        self.log.debug("Squid version: %d" % version)

        return version
