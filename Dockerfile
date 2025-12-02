FROM ghcr.io/infrasonar/python:3.12.9

ENV OPENSSL_CONF_PATH=/etc/ssl/openssl.cnf
RUN if [ -f "$OPENSSL_CONF_PATH" ]; then \
        cp "$OPENSSL_CONF_PATH" "$OPENSSL_CONF_PATH.bak" && \
        \
        # Use sed to add 'CipherString = DEFAULT@SECLEVEL=0' to the main configuration section.
        # This targets the [default_sect] or the main body of the config.
        # This tells OpenSSL to drop all security restrictions.
        sed -i '/\[default_sect\]/a CipherString = DEFAULT@SECLEVEL=0' "$OPENSSL_CONF_PATH" \
    ; else \
        echo "Error: openssl.cnf not found at $OPENSSL_CONF_PATH" && exit 1 \
    ; fi

ADD . /code
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]
