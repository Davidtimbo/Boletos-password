# Criptografia de boletos  
### Resumo/Objetivo
1. O programa foi criado a partir da necessidade de adicionar senhas aos boletos, já que estavam causando problemas para a empresa.
  Os boletos eram enviados com acesso liberado para qualquer um, permitindo que pessoas mal-intencionadas pudessem fazer modificações, como alterar o código QR ou a linha digitável do boleto.
  Agora, com a criptografia, o acesso ao boleto fica restrito apenas ao titular ou a quem possui o CPF/CNPJ específico, garantindo maior segurança e evitando fraudes.
  
2. Além disso, o programa foi desenvolvido para que os consultores da empresa possam enviar boletos de segunda via para os clientes, um trabalho que eles realizam manualmente.
  Para facilitar este processo, criei duas pastas específicas onde os boletos podem ser processados e protegidos com senha sem complicações.
  Para os boletos que não são segunda via e são enviados automaticamente, criei uma solução similar para criptografá-los. Dessa forma, agora todos os boletos estão sendo protegidos por senha.

 
 ### Este repositório contém dois scripts principais:

- **Script de Processamento e Criptografia de PDFs**: Este script em Python processa arquivos PDF em uma pasta de entrada especificada, extrai números de apartamento e prédio dos nomes dos arquivos, recupera o CPF/CNPJ correspondente de um banco de dados PostgreSQL, gera senhas de criptografia, criptografa os PDFs e move-os para uma pasta de saída.

- **Logger de Status do Serviço (service_status_logger.service)**: Este script em Bash verifica o status de um serviço systemd especificado e registra falhas em um arquivo de log especificado.

### Pré-requisitos
- Python 3.x
- Bibliotecas: ```psycopg2```, ```PyPDF2```
- Banco de dados ```PostgreSQL``` 
- Compartilhamento de rede montado em /mnt/consultores/

### Configuração
- O script requer a seguinte configuração:

   - **Conexão com o Banco de Dados**: Configure os detalhes da conexão com o banco de dados no dicionário db_config.
   - **Pastas**:
      - ```input_folder```: Pasta contendo os PDFs a serem processados.
      - ```output_folder```: Pasta onde os PDFs criptografados serão movidos.
      - ```temp_folder```: Pasta temporária usada durante o processo de criptografia.
 - Como Executar
 - Instalar Dependências:


### Detalhes do Script
- ```Classe PDFHandler```: Lida com o processamento, criptografia e gerenciamento de arquivos PDF.

  - ```process_pdfs()```: Processa todos os PDFs na pasta de entrada.
  - ```process_pdf(filepath)```: Processa um PDF individual.
  - ```get_cpfcnpj_by_unit(apartment, building)```: Consulta o banco de dados para obter o CPF/CNPJ com base nos números de apartamento e prédio.
  - ```get_password(cpf_cnpj)```: Gera uma senha de criptografia com base no CPF/CNPJ.
  - ```encrypt_pdf(input_pdf, output_pdf, password)```: Criptografa o PDF com a senha especificada.

- Funções Utilitárias:

  - ```change_permissions(input_folder)```: Altera as permissões de todos os PDFs na pasta de entrada.
  - **Loop Principal**: Monitora a pasta de entrada, altera permissões, processa PDFs e repete a cada 10 segundos.


### Exemplo de execução manual :
  - python3 **programa.py**
  - Este comando iniciará a monitoração da pasta de entrada, processará e criptografará PDFs e os moverá para a pasta de saída.

### Execução Contínua
 - Este script roda continuamente 24 horas por dia, pois foi criado o serviço "**boletocript.service**" no /etc/systemd/system. Com isso, o script é executado automaticamente e não precisa ser iniciado manualmente.


### Logger de Status do Serviço (service_status_logger.sh)
- Pré-requisitos
  - Serviço systemd para monitorar
  - Shell Bash

- Configuração
  - SERVICE_NAME: Nome do serviço systemd a ser monitorado.
  - LOG_FILE: Arquivo onde as falhas do serviço serão registradas.


- Detalhes do Script
  - Verifica o Status do Serviço: Usa ```systemctl``` para verificar se o serviço especificado falhou.
    - ex: ```systemctl status nome_do_seriço```
  - Registra Falhas: Se o serviço falhou, registra a falha com um carimbo de data/hora no arquivo de log especificado.

- exemplo:
  - ```./log_failure.sh``` (nome do shel criado para o log)
  - Este comando verificará o status do serviço especificado e registrará quaisquer falhas.
