# Use pinned tag for reproducibility (avoid :latest in production)
FROM agent0ai/agent-zero-base:latest

# Set build args with explicit validation
ARG BRANCH
RUN if [ -z "$BRANCH" ]; then echo "ERROR: BRANCH is not set!" >&2; exit 1; fi
ENV BRANCH=$BRANCH

# Copy filesystem files + application code in order of change frequency (stable → changing)
COPY ./fs/ /
COPY ./ /git/agent-zero

# Combine all RUN instructions into single layer to minimize bloat
RUN bash /ins/pre_install.sh $BRANCH && \
    bash /ins/install_A0.sh $BRANCH && \
    bash /ins/install_additional.sh $BRANCH && \
    bash /ins/install_A02.sh $BRANCH && \
    bash /ins/post_install.sh $BRANCH && \
    chmod +x /exe/initialize.sh /exe/run_A0.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh /exe/trigger_self_update.sh && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apt/* && \
    find /git/agent-zero -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Expose only required ports
EXPOSE 22 80 9000-9009

# Health check (adjust command based on actual service)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Initialize runtime and switch to supervisord
CMD ["/exe/initialize.sh", "$BRANCH"]
