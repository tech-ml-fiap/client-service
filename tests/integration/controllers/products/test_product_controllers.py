import pytest
from fastapi.testclient import TestClient

from app.domain.entities.product import Product
from app.shared.enums.categorys import CategoryEnum
from main import app

client = TestClient(app)

def test_list_products_empty(mocker):
    """
    Testa o endpoint GET /api/products quando não há produtos.
    """
    # Patch na referência usada no controlador
    mock_repo = mocker.patch("app.adapters.driver.controllers.product.product_controller.ProductRepository")
    mock_repo_instance = mock_repo.return_value
    mock_repo_instance.find_all.return_value = []

    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.json() == []  # Lista vazia



def test_create_product_success(mocker):
    """
    Testa o endpoint POST /api/products criando um produto com sucesso.
    """
    # Patch na referência usada no controlador
    mock_repo = mocker.patch("app.adapters.driver.controllers.product.product_controller.ProductRepository")
    mock_repo_instance = mock_repo.return_value

    # Use a entidade de domínio real para simular o retorno do repositório
    mock_repo_instance.create.return_value = Product(
        id=123,
        name="Produto Teste",
        description="Desc",
        price=100.0,
        category=CategoryEnum.LUNCH,
        quantity_available=10
    )

    payload = {
        "name": "Produto Teste",
        "description": "Desc",
        "price": 100.0,
        "category": "Lanche",
        "quantity_available": 10
    }

    response = client.post("/api/products", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == 123
    assert data["name"] == "Produto Teste"

    # Verifica se o repositório foi chamado
    mock_repo_instance.create.assert_called_once()


def test_create_product_negative_price(mocker):
    """
    Testa o endpoint POST /api/products quando o preço é negativo,
    esperando erro 400.
    """
    mock_repo = mocker.patch("app.adapters.driver.controllers.product.product_controller.ProductRepository")
    mock_repo_instance = mock_repo.return_value

    # O service lançaria ValueError, simulamos isso
    from app.domain.services.products.create_product_service import CreateProductService
    mocker.patch.object(CreateProductService, "execute", side_effect=ValueError("Price cannot be negative."))

    payload = {
        "name": "Produto Invalido",
        "description": "Teste",
        "price": -50.0,
        "category": "Lanche",
        "quantity_available": 5
    }

    response = client.post("/api/products", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Price cannot be negative."
    # repositório não deve ser chamado
    mock_repo_instance.create.assert_not_called()


def test_update_product_not_found(mocker):
    """
    Testa o endpoint PUT /api/products/{product_id} quando o produto não é encontrado.
    """
    mock_repo = mocker.patch("app.adapters.driver.controllers.product.product_controller.ProductRepository")
    mock_repo_instance = mock_repo.return_value

    # Simula que o service lança ValueError("Product not found")
    from app.domain.services.products.update_product_service import UpdateProductService
    mocker.patch.object(UpdateProductService, "execute", side_effect=ValueError("Product not found"))

    payload = {
        "name": "Produto Editado",
        "description": "Nova Desc",
        "price": 200.0,
        "category": "Lanche",
        "quantity_available": 5
    }

    response = client.put("/api/products/999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

    mock_repo_instance.update.assert_not_called()


def test_delete_product_success(mocker):
    """
    Testa o endpoint DELETE /api/products/{product_id} com sucesso.
    """
    mock_repo = mocker.patch("app.adapters.driver.controllers.product.product_controller.ProductRepository")
    mock_repo_instance = mock_repo.return_value

    # Simula que o service não levanta erro (produtos existe)
    from app.domain.services.products.delete_product_service import DeleteProductService
    mocker.patch.object(DeleteProductService, "execute", return_value=None)

    response = client.delete("/api/products/1")
    assert response.status_code == 204
    assert response.text == ""

    # Verifica se o service foi chamado; se quiser,
    # também pode checar se o repository foi chamado.
