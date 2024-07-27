import os
import psycopg2
import shutil
from PyPDF2 import PdfReader, PdfWriter
import time
import subprocess

# Configurações de conexão com o banco de dados
db_config = {
    'dbname': '*****',
    'user': '*****',
    'password': '*****',
    'host': '*****',
    'port': '*****'
}

class PDFProcessor:
    def __init__(self, input_folder, output_folder, temp_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        self.cpf_cnpj_password_map = {}  # Dicionário para armazenar senhas geradas por CPF/CNPJ
    
    def check_and_process_pdfs(self):
        for filename in os.listdir(self.input_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.input_folder, filename)
                try:
                    self.process_pdf(filepath)
                except Exception as e:
                    print(f'Erro ao processar {filename}: {e} :Ignorando')
    
    def process_pdf(self, filepath):
        filename = os.path.basename(filepath)
        
        # Remover a extensão e obter o nome do arquivo
        name_without_extension = filename.split('.')[0]
        
        # Verificar se o nome do arquivo tem pelo menos 5 dígitos para prédio
        if len(name_without_extension) < 5:
            print(f'Formato de arquivo inválido: {filename}')
            return
        
        # Extrair números do apartamento e prédio conforme o comprimento do nome do arquivo
        if len(name_without_extension) >= 11:
            apartment_str = name_without_extension[:6].lstrip('0') or '0'  # Alterado para pegar os primeiros 6 dígitos
            building_str = name_without_extension[6:11].lstrip('0') or '0'
        else:
            apartment_str = name_without_extension[:len(name_without_extension) - 5].lstrip('0') or '0'
            building_str = name_without_extension[-5:].lstrip('0') or '0'
        
        # Converter para inteiros
        apartment = int(apartment_str)
        building = int(building_str)

        print(f'\nProcessando arquivo: {filename}')
        print(f'Apartamento extraído: {apartment}')
        print(f'Prédio extraído: {building}')
        
        cpf_cnpj = get_cpfcnpj_by_unit(apartment, building)
        if not cpf_cnpj:
            print(f'Informações não encontradas para o arquivo {filename}\n')
            return
        
        if cpf_cnpj not in self.cpf_cnpj_password_map:
            password = get_password(cpf_cnpj)
            if password:
                self.cpf_cnpj_password_map[cpf_cnpj] = password
            else:
                print(f'CPF ou CNPJ inválido para o arquivo {filename}')
                return
        else:
            password = self.cpf_cnpj_password_map[cpf_cnpj]
        
        temp_pdf = os.path.join(self.temp_folder, filename)
        output_pdf = os.path.join(self.output_folder, filename)
        
        try:
            encrypt_pdf(filepath, temp_pdf, password)
        except Exception as e:
            print(f'Erro ao criptografar {filename}: {e}')
            return
        
        if not os.path.exists(temp_pdf):
            print(f'Arquivo temporário {temp_pdf} não foi criado.')
            return
        
        try:
            shutil.move(temp_pdf, output_pdf)
            os.remove(filepath)
        except FileNotFoundError as e:
            print(f'Erro ao mover ou remover o arquivo {filename}: {e}')
        except Exception as e:
            print(f'Erro inesperado ao mover ou remover o arquivo {filename}: {e}')
        
        print(f'{filename} foi criptografado com a senha {password}\n')
        
    def adjust_permissions(self):
        # Ajusta as permissões de todos os arquivos PDF na pasta de entrada para 777.
        for filename in os.listdir(self.input_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.input_folder, filename)
                try:
                    command = f'sudo su -c "chmod 777 \\"{filepath}\\""'
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f'Erro ao ajustar permissões do arquivo {filepath}: {e}')
                    
    def adjust_output_permissions(self):
        # Ajusta as permissões de todos os arquivos PDF na pasta de saída para 777.
        for filename in os.listdir(self.output_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.output_folder, filename)
                try:
                    command = f'sudo su -c "chmod 777 \\"{filepath}\\""'
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f'Erro ao ajustar permissões do arquivo {filepath}: {e}')               

def get_cpfcnpj_by_unit(apartment, building):
    query = """
    SELECT 
        up.cpf_cnpj
    FROM 
        unidades_predio up
    WHERE 
        up.cod_predio = %s AND up.unidade = %s;
    """
    
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            print(f'Executando consulta para prédio: {building}, apartamento: {apartment}')
            cur.execute(query, (building, apartment))
            result = cur.fetchone()
            if result:
                return result[0]  # Retorna o CPF/CNPJ
            else:
                return None

def get_password(cpf_cnpj):
    if len(cpf_cnpj) == 14 and cpf_cnpj.startswith('000'):  # Se for um CPF
        password = cpf_cnpj[3:8]
    elif len(cpf_cnpj) == 14:  # Se for um CNPJ
        password = cpf_cnpj[:5]
    else:
        print("CPF ou CNPJ inválido.")
        return None
    return password

def encrypt_pdf(input_pdf, output_pdf, password):
    pdf_writer = PdfWriter()
    pdf_reader = PdfReader(input_pdf)
    
    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])
    
    pdf_writer.encrypt(password)
    
    with open(output_pdf, 'wb') as fh:
        pdf_writer.write(fh)

def main():
    input_folder = '*****'
    output_folder = '*****'
    temp_folder = '*****'

    os.makedirs(temp_folder, exist_ok=True)
    
    processor = PDFProcessor(input_folder, output_folder, temp_folder)

    print('\nMonitorando a pasta:', input_folder)
    
    try:
        while True:
            processor.adjust_permissions()  # Ajustar permissões antes de processar
            processor.check_and_process_pdfs()
            processor.adjust_output_permissions()  # Ajustar permissões na pasta de saída
            time.sleep(10)  # Intervalo de 10 segundos entre as verificações
    except KeyboardInterrupt:
        print('\nMonitoramento interrompido pelo usuário.')

if __name__ == '__main__':
    main()

