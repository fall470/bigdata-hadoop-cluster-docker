FROM apache/hadoop:3.4.1

USER root

# Utiliser les archives CentOS 7
RUN sed -i 's|^mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-Base.repo && \
    sed -i 's|^#baseurl=http://mirror.centos.org/centos/$releasever/|baseurl=https://vault.centos.org/7.9.2009/|g' /etc/yum.repos.d/CentOS-Base.repo

# Installer Python 3
RUN yum --disablerepo=epel -y install python3 && \
    yum clean all

# Configuration embarquée : même config sur tous les nœuds
COPY conf/*.xml /opt/hadoop/etc/hadoop/

