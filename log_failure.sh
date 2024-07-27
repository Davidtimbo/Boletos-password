#!/bin/bash

SERVICE_NAME="boletos_cript.service"
LOG_FILE="/var/log/boletoscript_failure.log"

# Verifica o status do serviço
status=$(systemctl is-failed $SERVICE_NAME)

# Se o serviço falhou, registra no log
if [ "$status" == "failed" ]; then
    echo "$(date): $SERVICE_NAME falhou" >> $LOG_FILE
fi

