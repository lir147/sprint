import pytest
import json
from app import app, db_handler

# ----------------- Настройка тестового клиента -----------------
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ----------------- Фикстура для чистой записи в БД -----------------
@pytest.fixture
def new_pereval():
    raw_data = {
        "beautyTitle": "пер. Test",
        "title": "Тестовый",
        "user": {"email": "testuser@example.com", "phone": "+79000000000", "fio": "Тест Тестов"},
        "coords": {"latitude": "45.0", "longitude": "7.0", "height": "1000"}
    }
    images = [{"url": "test1.jpg"}, {"url": "test2.jpg"}]
    pereval_id = db_handler.add_pereval(raw_data, images)
    yield pereval_id
    # Удаляем перевал после теста
    db_handler.delete_pereval(pereval_id)

# ----------------- Тесты DatabaseHandler -----------------
def test_add_pereval(new_pereval):
    assert isinstance(new_pereval, int)

def test_get_pereval_by_id(new_pereval):
    pereval = db_handler.get_pereval_by_id(new_pereval)
    assert pereval['id'] == new_pereval
    assert 'raw_data' in pereval

def test_update_pereval(new_pereval):
    updated_data = {"raw_data": {"title": "Обновлённый тест"}}
    success, message = db_handler.update_pereval(new_pereval, updated_data)
    assert success is True
    updated_pereval = db_handler.get_pereval_by_id(new_pereval)
    assert updated_pereval['raw_data']['title'] == "Обновлённый тест"

def test_update_protected_field(new_pereval):
    updated_data = {"raw_data": {"fio": "Новое ФИО"}}
    success, message = db_handler.update_pereval(new_pereval, updated_data)
    assert success is False
    assert "редактировать нельзя" in message

def test_get_perevals_by_email(new_pereval):
    test_email = "testuser@example.com"
    perevals = db_handler.get_perevals_by_email(test_email)
    assert any(p['id'] == new_pereval for p in perevals)

# ----------------- Тесты REST API -----------------
def test_submit_data_api(client):
    payload = {
        "raw_data": {"title": "API Test", "user": {"email": "api@test.com"}},
        "images": []
    }
    response = client.post('/submitData', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'pereval_id' in data
    # Удаляем тестовый перевал
    db_handler.delete_pereval(data['pereval_id'])

def test_get_pereval_api(client, new_pereval):
    response = client.get(f'/submitData/{new_pereval}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == new_pereval

def test_patch_pereval_api(client, new_pereval):
    updated_data = {"raw_data": {"title": "API PATCH Test"}}
    response = client.patch(f'/submitData/{new_pereval}', json=updated_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['state'] == 1
    updated = db_handler.get_pereval_by_id(new_pereval)
    assert updated['raw_data']['title'] == "API PATCH Test"

def test_get_perevals_by_email_api(client, new_pereval):
    test_email = "testuser@example.com"
    response = client.get(f'/userPerevals?user__email={test_email}')
    assert response.status_code == 200
    data = response.get_json()
    assert any(p['id'] == new_pereval for p in data)
