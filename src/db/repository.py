"""Funções de leitura e gravação no banco (camada de "repositório").

Mantém a lógica de banco separada do resto do código: quem quiser salvar um
documento coletado chama save_scraped_document(...) e não precisa saber de
sessões, commits, etc.
"""

from __future__ import annotations

from db.models import ScrapedDocument
from db.session import SessionLocal


def save_scraped_document(
    startup_name: str,
    source_url: str,
    raw_text: str,
    source_type: str = "site_oficial",
) -> int:
    """Insere uma linha em scraped_documents e devolve o id gerado pelo banco.

    Args:
        startup_name: nome da startup.
        source_url: URL de onde o texto veio (a fonte rastreável).
        raw_text: o texto limpo já extraído.
        source_type: tipo da fonte (padrão: "site_oficial").
    """
    # "with" abre a sessão e garante que ela seja fechada no fim, mesmo se
    # acontecer um erro no meio do caminho.
    with SessionLocal() as session:
        # 1) Cria o objeto Python que representa a futura linha da tabela.
        doc = ScrapedDocument(
            startup_name=startup_name,
            source_url=source_url,
            raw_text=raw_text,
            source_type=source_type,
        )
        # 2) Adiciona o objeto à sessão e dá commit (confirma a gravação).
        session.add(doc)
        session.commit()
        # 3) Após o commit, o banco já gerou o id (e o fetched_at). O refresh
        #    recarrega esses valores do banco para dentro do objeto.
        session.refresh(doc)
        return doc.id
