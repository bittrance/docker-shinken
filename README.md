Docker Shinken geared to Kubernetes
===================================

This is a Docker image with a single-node Shinken container running
version 2.4.3 (actually master 73e7acb) with WebUI 2.4.2c. 

The container needs to be augmented with:

1) a mongodb container (currently allowing access without user/pass)
2) a provider of X-Remote-User header (e.g. Doorman) **This means that
exposing it directly to the Internet is a security risk**.

to form a full installation.

This image is geared towards Kubernetes support. An [example Kubernetes
setup](kubernetes/) is included for using Google Apps OAuth.

In Kubernetes, getting at the Docker host is discouraged. We therefore
need some method to update the configuration without recreating the
pod. (If you have e.g. an NFS server that you can mount as config volume,
that would work, but setting up NFS purely for this would be overkill.)

In order to update the configuration remotely, there is a script that
accepts a config tar ball and updates the configuration. This is how
you use it:
```
tar cf - . | kubectl exec shinken -i -- catcher --reload='supervisorctl restart shinken-arbiter' /etc/shinken/custom_configs
```

License and attribution
-----------------------
This software is released under [MIT License](LICENSE.md).

This repo is a fork of https://github.com/rohit01/docker_shinken adapted
to Shinken 2.4 and in particular replacing Thruk with Shinken WebUI 2.
Parts Copyright https://github.com/rohit01 2015.
