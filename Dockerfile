# Shinken Docker installation using pip (latest)
FROM        debian:wheezy
MAINTAINER  https://github.com/bittrance

# Install Shinken, Nagios plugins and supervisord
RUN         apt-get update && apt-get install -y python-pip \
                python-pycurl \
                python-cherrypy3 \
                python-dev \
                nagios-plugins \
                libsys-statistics-linux-perl \
                supervisor \
                libssl-dev \
                python-crypto \
                ntp git
RUN         useradd --create-home shinken && \
                pip install bottle pymongo requests arrow && \
                pip install git+https://github.com/naparuba/shinken.git@master && \
                update-rc.d -f shinken remove

# Install shinken modules from shinken.io
RUN         chown -R shinken:shinken /etc/shinken/ && \
                su - shinken -c 'shinken --init' && \
                su - shinken -c 'shinken install webui2' && \
                su - shinken -c 'shinken install auth-cfg-password' && \
                su - shinken -c 'shinken install booster-nrpe' && \
                su - shinken -c 'shinken install mongo-logs'

# Using a dir for this makes it easier to use kubernetes secret resources
RUN         install -m 0700 -o shinken -g shinken -d /var/lib/shinken/secrets

# Waiting for pull requests to go through
RUN        su - shinken -c 'git clone https://github.com/shinken-monitoring/mod-retention-mongodb /tmp/mod-retention-mongodb' && \
                su - shinken -c 'shinken install --local /tmp/mod-retention-mongodb'

# Install check_nrpe plugin
ADD         nrpe-2.15.tar.gz /usr/src/
RUN         cd /usr/src/nrpe-2.15/ && \
                ./configure --with-nagios-user=shinken --with-nagios-group=shinken --with-nrpe-user=shinken --with-nrpe-group=shinken --with-ssl=/usr/bin/openssl --with-ssl-lib=/usr/lib/x86_64-linux-gnu && \
                make all && \
                make install-plugin && \
                mv /usr/local/nagios/libexec/check_nrpe /usr/lib/nagios/plugins/check_nrpe && \
                cd / && \
                rm -rf /usr/src/nrpe-2.15

# Configure Shinken modules
RUN         rm /etc/shinken/contacts/*.cfg
ADD         shinken/shinken.cfg /etc/shinken/shinken.cfg
ADD         shinken/broker-master.cfg /etc/shinken/brokers/broker-master.cfg
ADD         shinken/poller-master.cfg /etc/shinken/pollers/poller-master.cfg
ADD         shinken/scheduler-master.cfg /etc/shinken/schedulers/scheduler-master.cfg
ADD         shinken/webui2.cfg /etc/shinken/modules/webui2.cfg
ADD         shinken/mongo-logs.cfg /etc/shinken/modules/mongo-logs.cfg
RUN         mkdir -p /etc/shinken/custom_configs /usr/local/custom_plugins && \
                chown -R shinken:shinken /etc/shinken/

# For pushing configuration across kubectl
ADD         catcher.py /usr/bin/catcher
RUN         chmod 755 /usr/bin/catcher

# Copy extra NRPE plugins and fix permissions
ADD         extra_plugins/* /usr/lib/nagios/plugins/
RUN         cd /usr/lib/nagios/plugins/ && \
                chmod a+x * && \
                chmod u+s check_apt restart_service check_ping check_icmp check_fping apt_update

# Define mountable directories
VOLUME      ["/etc/shinken/custom_configs", "/usr/local/custom_plugins"]

# configure supervisor
ADD         supervisor/conf.d/* /etc/supervisor/conf.d/

EXPOSE  7767

# Default docker process
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
