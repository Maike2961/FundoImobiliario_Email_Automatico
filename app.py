from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.message import EmailMessage
from dotenv import load_dotenv
import smtplib
import time
import os

load_dotenv(override=True)
driver = webdriver.Chrome()
info = []

def pegar_informacoes(site, fii_name):
    driver.maximize_window()
    driver.get(site)
    time.sleep(2)
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/section[1]/div/div/div[1]/div/form/div/span/input[2]').send_keys(fii_name)
    button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/div/section[1]/div/div/div[1]/div/form/div/button')))
    button.click()
    time.sleep(2)
    button2 = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/main/section/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div/div/a')))
    button2.click()
    time.sleep(5)
    try:
        dados_basicos = driver.find_element(By.XPATH, '//*[@id="cards-ticker"]')
        dados_do_fundo = dados_basicos.find_elements(By.TAG_NAME, 'span')
        dados_do_fundo_mes = [dados.text for dados in dados_do_fundo]
        nome_fundo = dados_do_fundo_mes[0]
        preco = dados_do_fundo_mes[1]
        dy12m = dados_do_fundo_mes[3]
        pvp = dados_do_fundo_mes[5]
        liquidez_diaria = dados_do_fundo_mes[7]
        variacao12m = dados_do_fundo_mes[9]
        tabela = driver.find_element(By.XPATH, '//*[@id="table-compare-fiis"]')
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", tabela)
        button3 = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="compare-section"]/div/div/button')))
        driver.execute_script("arguments[0].click()", button3)
        nome = tabela.find_elements(By.TAG_NAME, 'tr')      
        for names in nome[1:]:
            linha = names.find_elements(By.TAG_NAME, 'td')
            dados = [linhas.text for linhas in linha]
            info.append(dados)
        return info, nome_fundo, preco, dy12m, pvp, liquidez_diaria, variacao12m
    except Exception as e:
        print(e)
        return None
    
def enviar_email(conteudo, destinatario, nome_fundo, preco, dy12m, pvp, liquidez_diaria, variacao12m):
    print('Criando o email para as informações')
    EMAIL_ADRESS = os.getenv("EMAIL_ADRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL_ADRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("Variaveis não definidas")
    
    mensagem = f""" 
    <html>
        <body>
            <h2>Informacoes do fundo e comparando com outros</h2>
            <table border="1" style="width:100%; border-collapse:collapse; text-align:center">
                <tr>
                    <th>Nome</th>
                    <th>Preço</th>
                    <th>DY (12M)</th>
                    <th>P/VP</th>
                    <th>Liquidez</th>
                    <th>variação 12M</th>
                </tr>
                <tr>
                    <td>{nome_fundo}</td>
                    <td>{preco}</td>
                    <td>{dy12m}</td>
                    <td>{pvp}</td>
                    <td>{liquidez_diaria}</td>
                    <td>{variacao12m}</td>
                </tr>
                <hr>
                <tr>
                    <th>Fundo</th>
                    <th>DY (12M)</th>
                    <th>P/VP</th>
                    <th>Patrimônio</th>
                    <th>Tipo</th>
                    <th>Ativo</th>
                </tr>
    """
    for sublista in conteudo:
        mensagem += "<tr>"
        for item in sublista: 
            mensagem += f"<td>{item}</td>"
        mensagem+="</tr>"

    mensagem += """ 
            </table>
        </body>
    </html>
    """
    mail = EmailMessage()
    mail['Subject'] = 'Fundo Imobiliários'
    mail['From'] = EMAIL_ADRESS
    mail['To'] = destinatario
    mail.add_header('Content-Type', 'text/html')
    mail.set_payload(mensagem.encode('utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', '465') as smtp:
        smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
        smtp.send_message(mail)
        print('Email Enviado')

def inciar_automacao():
    fundo_name = "MXRF11"
    site_name = "https://investidor10.com.br/"
    destinatario = ""

    conteudo, nome_fundo, preco, dy12m, pvp, liquidez_diaria, variacao12m  = pegar_informacoes(site_name, fundo_name)

    if conteudo and destinatario:
        enviar_email(conteudo, destinatario, nome_fundo, preco, dy12m, pvp,liquidez_diaria, variacao12m) 


if __name__ == "__main__":
    print("Iniciando...")
    inciar_automacao()



