# Use kali-rolling (production tag doesn't exist in public registry)
FROM kalilinux/kali-rolling

# Set locale and timezone in single layer to reduce image size
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    TZ=UTC \
    DEBIAN_FRONTEND=noninteractive

# Copy contents of the project to / first (before apt) for better caching when this changes
COPY ./fs/ /

# Install packages + locales + timezone in single RUN layer with aggressive cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    tzdata && \
    sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8 && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    bash /ins/install_base_packages1.sh && \
    bash /ins/install_base_packages2.sh && \
    bash /ins/install_base_packages3.sh && \
    bash /ins/install_base_packages4.sh && \
    bash /ins/install_python.sh && \
    bash /ins/install_searxng.sh && \
    bash /ins/configure_ssh.sh && \
    bash /ins/after_install.sh && \
    apt-get purge -y --auto-remove locales tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/log/* && \
    find / -name '*.py[cod]' -delete && \
    find / -type d -name __pycache__ -delete

# Health check for base image (optional, can be overridden in run image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD test -f /sys/class/net/eth0/address || exit 1

CMD ["tail", "-f", "/dev/null"]
