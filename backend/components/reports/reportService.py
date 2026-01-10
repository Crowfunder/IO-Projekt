from backend.app import db
from backend.database.models import Entry, Worker
from sqlalchemy import or_
from datetime import datetime, time
from typing import List, Tuple, Optional

def get_report_data(date_from: datetime = None,
                    date_to: datetime = None,
                    worker_id: int = None,
                    show_valid: bool = False,
                    show_invalid: bool = False) -> List[Tuple[Entry, Optional[Worker]]]:
    """
    Pobiera dane do raportu wejść, łącząc wpisy z tabeli Entry z danymi pracowników.

    Funkcja obsługuje filtrowanie po zakresie dat, konkretnym pracowniku oraz statusie
    poprawności wejścia. Wyniki są sortowane malejąco po dacie.

    Args:
        date_from (datetime, optional): Data początkowa (włącznie). Domyślnie None.
        date_to (datetime, optional): Data końcowa (włącznie). Domyślnie None.
        worker_id (int, optional): ID pracownika, dla którego pobrać raport. Domyślnie None.
        show_valid (bool, optional): Czy uwzględniać poprawne wejścia (kod 0).
            Jeśli zaznaczone razem z show_invalid (lub oba odznaczone), zwraca wszystkie typy.
        show_invalid (bool, optional): Czy uwzględniać niepoprawne wejścia (kod != 0).
            Jeśli zaznaczone razem z show_valid (lub oba odznaczone), zwraca wszystkie typy.

    Returns:
        List[Tuple[Entry, Optional[Worker]]]: Lista krotek, gdzie pierwszy element to obiekt wpisu (Entry),
        a drugi to obiekt pracownika (Worker) lub None, jeśli wpis nie ma przypisanego pracownika.
    """
    query = db.session.query(Entry, Worker).outerjoin(Worker, Entry.worker_id == Worker.id)

    if date_from:
        query = query.filter(Entry.date >= date_from)

    if date_to:
        query = query.filter(Entry.date <= date_to)

    if worker_id:
        query = query.filter(Entry.worker_id == worker_id)

    # Logika filtrów:
    # 1. Oba zaznaczone -> Pokaż wszystko (pass)
    # 2. Tylko valid -> kod == 0
    # 3. Tylko invalid -> kod != 0
    # 4. Żaden niezaznaczony -> Pokaż wszystko (domyślne zachowanie query bez filtrów)
    if show_valid and show_invalid:
        pass
    elif show_valid:
        query = query.filter(Entry.code == 0)
    elif show_invalid:
        query = query.filter(Entry.code != 0)

    query = query.order_by(Entry.date.desc())

    return query.all()