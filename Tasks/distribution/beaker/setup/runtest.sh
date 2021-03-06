#!/bin/bash

# Copyright (c) 2006 Red Hat, Inc. All rights reserved. This copyrighted material 
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General
# Public License v.2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Author: Bill Peck <bpeck@redhat.com>

# source the test script helpers
. /usr/bin/rhts-environment.sh
. /usr/share/beakerlib/beakerlib.sh

function BuildBeaker ()
{
    rlPhaseStartTest "Build Beaker from git"
    rlRun "git clone git://git.beaker-project.org/beaker"
    rlRun "pushd beaker"
    rlRun "git checkout ${BEAKER_GIT_REF:-develop}"
    if [[ -n "$BEAKER_GIT_REMOTE" ]] ; then
        rlRun "git fetch $BEAKER_GIT_REMOTE ${BEAKER_GIT_REMOTE_REF:-develop}"
        rlRun "git ${BEAKER_GIT_REMOTE_MERGE:-checkout} FETCH_HEAD" \
            || rlDie "Git checkout/merge failed"
    fi
    rlRun "yum-builddep -y ./beaker.spec"
    rlRun "yum -y install tito"
    rlRun "tito build --rpm --test" || rlDie "Tito RPM build failed"
    rlRun "popd"
    rlRun "createrepo /tmp/tito/noarch/"
    cat >/etc/yum.repos.d/beaker-local-builds.repo <<"EOF"
[tito]
name=tito
baseurl=file:///tmp/tito/noarch/
EOF
    rlAssert0 "Created yum repo config for /tmp/tito/noarch/" $?
    rlPhaseEnd
}

function InstallInventory_git()
{
    rlRun "yum install --nogpg -y beaker-server"
}

function InstallInventory_repo()
{
    rlRun "yum install -y beaker-server$VERSION"
}

function InstallLabController_git()
{
    rlRun "yum install --nogpg -y beaker-lab-controller beaker-lab-controller-addDistro"
}

function InstallLabController_repo()
{
    rlRun "yum install -y beaker-lab-controller$VERSION"
    rlRun "yum install -y beaker-lab-controller-addDistro$VERSION"
}

function generate_rsync_cfg()
{
    rlRun "mkdir -p /var/www/html/beaker-logs"
    rlRun "chown nobody /var/www/html/beaker-logs"
    rlRun "chmod 755 /var/www/html/beaker-logs"
    cat <<__EOF__ > /etc/rsyncd.conf
use chroot = false

[beaker-logs]
	path = /var/www/html/beaker-logs
	comment = beaker logs
	read only = false
__EOF__
    rlAssert0 "Wrote rsyncd.conf" $?
}

function generate_proxy_cfg()
{
    cat << __EOF__ > /etc/beaker/labcontroller.conf
HUB_URL = "https://$SERVER/bkr/"
AUTH_METHOD = "password"
USERNAME = "host/$HOSTNAME"
PASSWORD = "testing"
CACHE = True
ARCHIVE_SERVER = "http://$SERVER/beaker-logs"
ARCHIVE_BASEPATH = "/var/www/html/beaker"
ARCHIVE_RSYNC = "rsync://$SERVER/beaker-logs"
RSYNC_FLAGS = "-arv --timeout 300"
QPID_BUS=False
__EOF__
    rlAssert0 "Wrote /etc/beaker/labcontroller.conf" $?
}

function generate_client_cfg() {
    cat <<__EOF__ >/etc/beaker/client.conf
HUB_URL = "http://$SERVER/bkr"
AUTH_METHOD = "password"
USERNAME = "admin"
PASSWORD = "testing"
__EOF__
    rlAssert0 "Wrote /etc/beaker/client.conf" $?
}

function Inventory()
{
    rlPhaseStartTest "Install database"
    rlRun "yum install -y mysql-server MySQL-python" 0
    # Backup /etc/my.cnf and make INNODB the default engine.
    rlRun "cp /etc/my.cnf /etc/my.cnf-orig" 0
    cat /etc/my.cnf-orig | awk '
        {print $1};
        /\[mysqld\]/ {
            print "default-storage-engine=INNODB";
            print "max_allowed_packet=50M";
            print "character-set-server=utf8";
            print ENVIRON["MYSQL_EXTRA_CONFIG"];
        }' > /etc/my.cnf
    rlAssert0 "Configured /etc/my.cnf" $?
    rlServiceStart mysqld
    rlRun "mysql -u root -e \"CREATE DATABASE beaker;\"" 0 "Creating database 'beaker'"
    rlRun "mysql -u root -e \"GRANT ALL ON beaker.* TO beaker@localhost IDENTIFIED BY 'beaker';\"" 0 "Granting privileges to the user 'beaker@localhost'"
    rlPhaseEnd

    rlPhaseStartTest "Install Beaker server"
    InstallInventory$SOURCE || rlDie "Installing Beaker server failed"
    rlPhaseEnd

    rlPhaseStartTest "Configure Beaker server"
    rlRun "mkdir -p /var/www/beaker/harness" 0 "in lieu of running beaker-repo-update"
    cat << __EOF__ > /etc/beaker/motd.txt
<span>Integration tests are running against this server</span>
__EOF__
    rlPhaseEnd

    if [ -n "$IMPORT_DB" ] ; then
        rlPhaseStartTest "Import database dump"
        rlRun "wget $IMPORT_DB" 0 "Retrieving remote DB"
        DB_FILE=echo $IMPORT_DB | perl -pe 's|.+/(.+\.xz)$|\1|'
        rlRun "xzcat $DB_FILE | mysql" 0 "Importing DB"
        rlPhaseEnd
    else
        rlPhaseStartTest "Initialize database"
        rlRun "beaker-init -u admin -p testing -e $SUBMITTER" 0
        rlPhaseEnd
    fi

    rlPhaseStartTest "Configure iptables"
    # XXX we can do better than this
    rlServiceStop iptables
    rlPhaseEnd

    if [ -n "$GRAPHITE_SERVER" ] ; then
        rlPhaseStartTest "Configure Beaker for Graphite"
        sed -i \
            -e "/^#carbon.address /c carbon.address = ('$GRAPHITE_SERVER', ${GRAPHITE_PORT:-2023})" \
            -e "/^#carbon.prefix /c carbon.prefix = '${GRAPHITE_PREFIX:+$GRAPHITE_PREFIX.}beaker.'" \
            /etc/beaker/server.cfg
        rlAssert0 "Added carbon settings to /etc/beaker/server.cfg" $?
        rlPhaseEnd
    fi

    rlPhaseStartTest "Start services"
    rlServiceStart httpd
    rlServiceStart beakerd
    rlPhaseEnd

    rlPhaseStartTest "Add lab controllers"
    rlRun "yum install -y python-twill"
    for CLIENT in $CLIENTS; do
        rlRun "./add-labcontroller.py -l $CLIENT" 0 "Add Lab Controller"
    done
    rlPhaseEnd

    rlPhaseStartTest "Enable rsync for fake archive server"
    generate_rsync_cfg
    rlRun "chkconfig rsync on" 0
    rlRun "service xinetd restart" 0
    rlPhaseEnd

    if [ -n "$ENABLE_COLLECTD" ] ; then
        rlPhaseStartTest "Enable collectd for metrics collection"
        rlRun "yum install -y collectd"
        cat >/etc/collectd.d/beaker-server.conf <<EOF
LoadPlugin processes
LoadPlugin write_graphite
<Plugin write_graphite>
  <Carbon>
    Host "$GRAPHITE_SERVER"
    Port "${GRAPHITE_PORT:-2023}"
    Prefix "${GRAPHITE_PREFIX:+$GRAPHITE_PREFIX/}host/"
  </Carbon>
</Plugin>
<Plugin processes>
  Process "beakerd"
  Process "httpd"
</Plugin>
EOF
        rlAssert0 "Wrote collectd config for Beaker server" $?
        rlRun "chkconfig collectd on"
        rlServiceStart collectd
        rlPhaseEnd
    fi

    rlPhaseStartTest "SERVERREADY"
    rlRun "rhts-sync-set -s SERVERREADY" 0 "Inventory ready"
    rlPhaseEnd
}

function LabController()
{
    rlPhaseStartTest "Install Beaker lab controller"
    InstallLabController$SOURCE || rlDie "Installing lab controller failed"
    rlPhaseEnd

    rlPhaseStartTest "Configure Beaker lab controller"
    # Configure beaker-proxy config
    generate_proxy_cfg
    # configure beaker client
    generate_client_cfg
    echo "add_distro=1" > /etc/sysconfig/beaker_lab_import
    rlPhaseEnd

    rlPhaseStartTest "Fetch netboot loaders"
    # Using cobbler to get the netboot loaders..
    rlServiceStart httpd cobblerd
    rlRun "cobbler get-loaders" 0 "get network boot loaders"
    rlRun "cobbler sync" 0 "sync boot loaders to tftpboot"
    rlServiceStop cobblerd
    rlPhaseEnd

    rlPhaseStartTest "Configure iptables"
    # XXX we can do better than this
    rlServiceStop iptables
    rlPhaseEnd

    rlPhaseStartTest "Wait for SERVERREADY"
    rlRun "rhts-sync-block -s SERVERREADY -s ABORT $SERVER" 0 "Wait for Server to become ready"
    rlPhaseEnd

    rlPhaseStartTest "Start services"
    rlRun "chkconfig xinetd on" 0
    rlRun "chkconfig tftp on" 0
    rlServiceStart xinetd
    # There is beaker-transfer as well but it's disabled by default
    for service in httpd beaker-proxy beaker-watchdog beaker-provision ; do
        rlRun "chkconfig $service on" 0
        rlServiceStart $service
    done
    rlPhaseEnd

    if [ -n "$ENABLE_BEAKER_PXEMENU" ] ; then
        rlPhaseStartTest "Enable PXE menu"
        cat >/etc/cron.hourly/beaker_pxemenu <<"EOF"
#!/bin/bash
exec beaker-pxemenu -q
EOF
        chmod 755 /etc/cron.hourly/beaker_pxemenu
        rlAssert0 "Created /etc/cron.hourly/beaker_pxemenu" $?
        rlPhaseEnd
    fi

    if [ -n "$ENABLE_COLLECTD" ] ; then
        rlPhaseStartTest "Enable collectd for metrics collection"
        rlRun "yum install -y collectd"
        cat >/etc/collectd.d/beaker-lab-controller.conf <<EOF
LoadPlugin processes
LoadPlugin write_graphite
<Plugin write_graphite>
  <Carbon>
    Host "$GRAPHITE_SERVER"
    Port "${GRAPHITE_PORT:-2023}"
    Prefix "${GRAPHITE_PREFIX:+$GRAPHITE_PREFIX/}host/"
  </Carbon>
</Plugin>
<Plugin processes>
  Process "beaker-proxy"
  Process "beaker-provisio"
  Process "beah_dummy.py"
</Plugin>
EOF
        rlAssert0 "Wrote collectd config for Beaker lab controller" $?
        rlRun "chkconfig collectd on"
        rlServiceStart collectd
        rlPhaseEnd
    fi
}

rlJournalStart

if [[ "$(getenforce)" == "Enforcing" ]] ; then
    rlLogWarning "SELinux in enforcing mode, Beaker is not likely to work!"
fi

if $(echo $CLIENTS | grep -q $HOSTNAME); then
    rlLog "Running as Lab Controller using Inventory: ${SERVERS}"
    SERVER=$(echo $SERVERS | awk '{print $1}')
    [[ $SOURCE == "_git" ]] && BuildBeaker
    LabController
fi

if $(echo $SERVERS | grep -q $HOSTNAME); then
    rlLog "Running as Inventory using Lab Controllers: ${CLIENTS}"
    [[ $SOURCE == "_git" ]] && BuildBeaker
    Inventory
fi

if [ -z "$SERVERS" -o -z "$CLIENTS" ]; then
    rlLog "Inventory=${SERVERS} LabController=${CLIENTS} Assuming Single Host Mode."
    CLIENTS=$STANDALONE
    SERVERS=$STANDALONE
    SERVER=$(echo $SERVERS | awk '{print $1}')
    [[ $SOURCE == "_git" ]] && BuildBeaker
    Inventory
    LabController
fi

rlPhaseStartCleanup
rlRun "rm -f /etc/yum.repos.d/beaker-local-builds.repo" 0
rlPhaseEnd

rlJournalEnd
rlJournalPrintText
