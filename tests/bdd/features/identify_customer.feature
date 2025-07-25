Feature: Identificar cliente por CPF
    Scenario: Cliente existente recebe JWT
        Given existe um cliente com CPF "12345678909"
        When eu faço uma requisição GET em "api/client/cpf/12345678909"
        Then a resposta tem status 200
        And o JSON contém o campo "jwt"
