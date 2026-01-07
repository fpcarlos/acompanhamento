# Projeto de Acompanhamento de Auditoria (esqueleto)

Este repositório contém um projeto Django minimal para acompanhamento de auditoria (`projeto_auditoria`) e a app `auditoria` com modelos básicos de `Audit` e `Finding`.

Instalação (PowerShell):

1. Ative o venv: `.\.venv\Scripts\Activate.ps1`
2. Instale dependências: `pip install -r requirements.txt`
3. Crie migrations e rode migrações:
	- `python manage.py makemigrations auditoria`
	- `python manage.py migrate`
4. Crie um superusuário (opcional): `python manage.py createsuperuser`
5. Rode o servidor: `python manage.py runserver`

Testes:

- Rodar testes com pytest: `pytest -q` (veja `pytest.ini` para configuração do DJANGO_SETTINGS_MODULE).

Notas:

- Este é um esqueleto inicial; se desejar que eu adicione endpoints REST, autenticação por token, ou fixtures e migrations iniciais, me informe que eu adiciono em um próximo PR.
