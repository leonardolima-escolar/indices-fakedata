import random
from faker import Faker
from faker.providers.address.pt_BR import Provider
import psycopg2
import datetime

fake = Faker('pt_BR')

# Conexão com o banco de dados
conn = psycopg2.connect(
    dbname="fakedata",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Configurar a quantidade de linhas que você deseja gerar para cada tabela
qtd_usuarios = 50000
qtd_empresas = 500
qtd_usuario_empresa = 50000
qtd_produtos = 200000
qtd_vendas = 50000
qtd_produto_vendas = 100000
qtd_endereco = 50000
qtd_cartaocredito = 45000
qtd_cardUser = 40000

# Gerar e inserir dados na tabela User
for _ in range(qtd_usuarios):
    # Não é garantia de ser único
    cursor.execute("INSERT INTO \"User\" (name, email, password, cpf, phone) VALUES (%s, %s, %s, %s, %s)",
                   (fake.name(), str(fake.random_int(1, qtd_usuarios)) + str(fake.random_int(1, qtd_usuarios)) + fake.email(), fake.password(), fake.cpf(), fake.numerify("##############")))

# Gerar e inserir dados na tabela Company
for _ in range(qtd_empresas):
    cursor.execute("INSERT INTO \"Company\" (name, cnpj, website) VALUES (%s, %s, %s)",
                   (fake.company(), fake.numerify("##############"),
                    fake.url()))

# Gerar e inserir dados na tabela UserCompany
cursor.execute("SELECT id FROM \"User\"")
user_ids = [row[0] for row in cursor.fetchall()]

for _ in range(qtd_usuario_empresa):
    # id não começou com 1
    user_id = fake.random_element(user_ids)
    company_id = random.randint(1, qtd_empresas)
    # Não é garantia de ser único
    cursor.execute(
        "SELECT COUNT(*) FROM \"UserCompany\" WHERE user_id = %s AND company_id = %s", (user_id, company_id))

    if cursor.fetchone()[0] > 0:
        continue

    cursor.execute("INSERT INTO \"UserCompany\" (user_id, company_id, is_employee) VALUES (%s, %s, %s)",
                   (user_id, company_id, fake.boolean()))


# Gerar e inserir dados na tabela Product
for _ in range(qtd_produtos):
    user_id = fake.random_element(user_ids)
    company_id = random.randint(1, qtd_empresas)

    cursor.execute("INSERT INTO \"Product\" (name, price, description, is_approved, created_by, company, category) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (fake.word(), round(random.uniform(1.0, 100.0), 2), fake.sentence() if random.choice([True, False]) else None, fake.boolean(), user_id, company_id, fake.word()))


# Gerar e inserir dados na tabela Sale
for _ in range(qtd_produtos):
    user_id = fake.random_element(user_ids)
    company_id = random.randint(1, qtd_empresas)

    cursor.execute("INSERT INTO \"Sale\" (user_id, company_id, is_delivered, payment_method, total, datetime) VALUES (%s, %s, %s, %s, %s, %s)",
                   (user_id, company_id, fake.boolean(), random.choice(["Cartão", "Boleto", "PIX"]), round(random.uniform(100.0, 1000.0), 2), fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')))


# Gerar e inserir dados na tabela ProductSale
cursor.execute("SELECT id FROM \"Sale\"")
sale_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM \"Product\"")
product_ids = [row[0] for row in cursor.fetchall()]

for _ in range(qtd_produto_vendas):
    sale_id = fake.random_element(sale_ids)
    product_id = fake.random_element(product_ids)

    # Não é garantia de ser único
    cursor.execute(
        "SELECT COUNT(*) FROM \"ProductSale\" WHERE product_id = %s AND sale_id = %s", (product_id, sale_id))

    if cursor.fetchone()[0] > 0:
        continue

    cursor.execute("INSERT INTO \"ProductSale\" (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                   (sale_id, product_id, random.randint(1, 100), round(random.uniform(1.0, 100.0), 2)))


# Gerar e inserir dados na tabela Card
for _ in range(qtd_cartaocredito):
    x = random.randint(0, 20)
    # nome do meio A. M. ou J. (abreviações cujo cartões de credito Brasileiro exigem)
    middle_name = ''
    if x < 10:  # 1 ou 2 nomes do meio
        middle_name = str(fake.bothify(text=' ?. ?. '))
    else:
        middle_name = str(fake.bothify(text=' ?. '))

    cursor.execute("INSERT INTO \"Card\" (name,number,date,cvc) VALUES (%s,%s,%s,%s)",
                   (str(str(fake.first_name())+middle_name+str(fake.last_name())), fake.credit_card_number(),
                    fake.credit_card_expire(), fake.credit_card_security_code()))


# Gerar e inserir dados na tabela UserCard
cursor.execute("SELECT id FROM \"Card\"")
card_ids = [row[0] for row in cursor.fetchall()]

for _ in range(qtd_cardUser):
    user_id = fake.random_element(user_ids)
    card_id = fake.random_element(card_ids)

    cursor.execute(
        "INSERT INTO \"UserCard\" (user_id,card_id) VALUES (%s,%s)", (user_id, card_id))

# Gerar e inserir dados na Address
for _ in range(qtd_endereco):
    user_id = fake.random_element(user_ids)

    cursor.execute("INSERT INTO \"Address\" (user_id, cep,uf, city, address1, address2) VALUES (%s,%s,%s,%s,%s,%s)",
                   (user_id, fake.bothify(text='#####-###'), fake.country(), fake.city(), fake.street_address(), fake.street_name()))


# Confirmar as alterações e fechar a conexão
conn.commit()
cursor.close()
conn.close()
