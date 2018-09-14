FROM garnet:0.0.1

RUN mkdir $HOME/logs && chown $USER $HOME/logs
USER $USER
WORKDIR $HOME

ENTRYPOINT ["/bin/bash", "sopelbot/docker-entrypoint.sh"]
CMD []
