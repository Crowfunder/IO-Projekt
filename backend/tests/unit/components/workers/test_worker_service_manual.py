import pytest
import os
import io
import numpy as np
import face_recognition
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.app import create_app, db
from backend.database.models import Worker
# Importujemy serwis
from backend.components.workers import workerService


# --- FIXTURY ---

@pytest.fixture
def app_context():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


# --- TESTY ---

def test_create_worker_embedding_from_file():
    """
    Testuje tworzenie embeddingu z prawdziwego pliku (testimg.jpg).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Ścieżka relatywna z backend/tests/unit/components/workers do backend/tests/assets
    image_path = os.path.normpath(os.path.join(current_dir, "../../../assets/testimg.jpg"))

    print(f"Szukam pliku pod adresem: {image_path}")
    if not os.path.exists(image_path):
        pytest.skip(f"Pominięto: Nie znaleziono pliku {image_path}")

    image_input = face_recognition.load_image_file(image_path)

    # Wywołanie funkcji z serwisu
    result_blob = workerService.create_worker_embedding(image_input)

    assert isinstance(result_blob, bytes)
    assert len(result_blob) > 0

    # Weryfikacja czy blob da się odczytać jako numpy array
    buffer = io.BytesIO(result_blob)
    embeddings = np.load(buffer, allow_pickle=True)

    assert len(embeddings) > 0, "Nie wykryto twarzy na zdjęciu testowym."
    assert len(embeddings[0]) == 128  # Face_recognition generuje wektory 128-wymiarowe


@patch('backend.components.workers.workerService.create_worker_embedding')
def test_create_worker_adds_to_db(mock_create_embedding, app_context):
    """
    Testuje czy funkcja create_worker poprawnie zapisuje pracownika w bazie.
    """
    mock_create_embedding.return_value = b'test_blob_data'
    name = "Jan Testowy"
    fake_image = MagicMock()  # Udajemy obrazek
    expiration = datetime(2025, 12, 31)

    with app_context.app_context():
        # create_worker zwraca obiekt Worker
        worker = workerService.create_worker(name, fake_image, expiration)

        assert worker.id is not None
        assert worker.name == name

        # Sprawdzamy czy zapisało się w bazie
        fetched_worker = db.session.get(Worker, worker.id)
        assert fetched_worker is not None
        assert fetched_worker.name == "Jan Testowy"
        assert fetched_worker.face_embedding == b'test_blob_data'


def test_extend_worker_expiration_success(app_context):
    initial_date = datetime(2024, 1, 1)
    new_date = datetime(2030, 1, 1)

    with app_context.app_context():
        # 1. Przygotowanie danych w bazie
        worker = Worker(
            name="Marek DoZmiany",
            face_embedding=b'dummy_data',
            expiration_date=initial_date,
            secret="dummy_secret"
        )
        db.session.add(worker)
        db.session.commit()

        # Pobieramy obiekt pracownika (serwis wymaga obiektu, nie ID!)
        worker_to_update = db.session.get(Worker, worker.id)

        # 2. Wywołanie serwisu
        updated_worker = workerService.extend_worker_expiration(worker_to_update, new_date)

        # 3. Weryfikacja
        assert updated_worker.expiration_date == new_date

        # Odświeżenie sesji i sprawdzenie w bazie
        db.session.expire_all()
        fetched_worker = db.session.get(Worker, worker.id)
        assert fetched_worker.expiration_date == new_date


def test_update_worker_name_success(app_context):
    initial_name = "Jan Kowalski"
    new_name = "Jan Nowak"

    with app_context.app_context():
        worker = Worker(
            name=initial_name,
            face_embedding=b'dummy_data',
            expiration_date=datetime(2025, 12, 12),
            secret="dummy_secret"
        )
        db.session.add(worker)
        db.session.commit()

        # Pobieramy obiekt pracownika
        worker_to_update = db.session.get(Worker, worker.id)

        # Wywołanie serwisu (przekazujemy OBIEKT, nie ID)
        workerService.update_worker_name(worker_to_update, new_name)

        db.session.expire_all()
        fetched_worker = db.session.get(Worker, worker.id)
        assert fetched_worker.name == new_name


def test_update_worker_face_embedding_success(app_context):
    initial_name = "Test Face Update"
    initial_face_data = b'old_dummy_embedding'
    new_raw_image = b'new_raw_image_data_jpg'
    mocked_embedding_result = b'new_calculated_embedding_123'

    with app_context.app_context():
        worker = Worker(
            name=initial_name,
            face_embedding=initial_face_data,
            expiration_date=datetime(2025, 12, 12),
            secret="dummy_secret"
        )
        db.session.add(worker)
        db.session.commit()

        # Mockujemy funkcję generującą embedding wewnątrz serwisu
        with patch('backend.components.workers.workerService.create_worker_embedding') as mock_embedding:
            mock_embedding.return_value = mocked_embedding_result

            # Pobieramy obiekt pracownika
            worker_to_update = db.session.get(Worker, worker.id)

            # Wywołanie serwisu (przekazujemy OBIEKT, nie ID)
            workerService.update_worker_face_image(worker_to_update, new_raw_image)

            mock_embedding.assert_called_once_with(new_raw_image)

        db.session.expire_all()
        fetched_worker = db.session.get(Worker, worker.id)
        assert fetched_worker.face_embedding == mocked_embedding_result