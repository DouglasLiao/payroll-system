# API Documentation - Swagger/OpenAPI

## Acessando a Documentação

O sistema possui documentação interativa completa da API com **todas as fórmulas de cálculo** documentadas:

### Swagger UI (Recomendado)

Interface interativa para testar todos os endpoints:

```
http://localhost:8000/docs/
```

### ReDoc

Documentação alternativa (visual limpo):

```
http://localhost:8000/redoc/
```

### OpenAPI Schema (JSON/YAML)

Schema bruto para importar em Postman/Insomnia:

```
http://localhost:8000/schema/
```

---

## Fórmulas Documentadas

Todas as fórmulas de cálculo estão documentadas no Swagger:

### ✅ Valor da Hora

```
valor_hora = valor_contrato_mensal ÷ 220
```

### ✅ Adiantamento Quinzenal (padrão 40%)

```
adiantamento = valor_contrato_mensal × 0.40
```

### ✅ Horas Extras 50%

```
valor_hora_extra = valor_hora × 1.5
total_horas_extras = horas_extras × valor_hora_extra
```

### ✅ Horas em Feriado (100%)

```
valor_hora_feriado = valor_hora × 2.0
total_feriados = horas_feriado × valor_hora_feriado
```

### ✅ DSR (16.67%)

```
dsr = total_horas_extras × 0.1667
```

### ✅ Adicional Noturno (20%)

```
adicional_noturno = horas_noturnas × (valor_hora × 0.20)
```

### ✅ Descontos

```
desconto_atraso = (minutos ÷ 60) × valor_hora
desconto_falta = horas × valor_hora
dsr_sobre_faltas = desconto_falta × 0.1667
```

### ✅ Valor Final

```
proventos = saldo_base + horas_extras + feriados + dsr + adicional_noturno
descontos = atrasos + faltas + dsr_sobre_faltas + vt + manuais
líquido = proventos - descontos
```

---

## Exemplos de Request/Response

Todos os endpoints possuem exemplos práticos documentados no Swagger UI.

### Exemplo: Criar Folha de Pagamento

**POST** `/payrolls/calculate/`

```json
{
  "provider_id": 1,
  "reference_month": "01/2026",
  "overtime_hours_50": 10,
  "holiday_hours": 8,
  "night_hours": 20,
  "late_minutes": 30,
  "absence_hours": 8,
  "manual_discounts": 0,
  "notes": "Folha de janeiro"
}
```

**Response 201 Created:**

```json
{
  "id": 1,
  "provider_name": "João Silva",
  "reference_month": "01/2026",
  "base_value": "2200.00",
  "hourly_rate": "10.00",
  "advance_value": "880.00",
  "overtime_amount": "150.00",
  "holiday_amount": "160.00",
  "dsr_amount": "25.00",
  "night_shift_amount": "40.00",
  "total_earnings": "1695.00",
  "late_discount": "5.00",
  "absence_discount": "80.00",
  "dsr_on_absences": "13.33",
  "vt_discount": "202.40",
  "total_discounts": "300.73",
  "net_value": "1394.27",
  "status": "DRAFT"
}
```

---

## Como Usar

1. **Inicie o servidor Django:**

   ```bash
   cd backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Acesse o Swagger UI:**

   ```
   http://localhost:8000/docs/
   ```

3. **Teste os endpoints:**
   - Cada endpoint possui um botão "Try it out"
   - Preencha os parâmetros
   - Clique em "Execute"
   - Veja o resultado em tempo real

---

## Endpoints Disponíveis

### Providers (Prestadores)

- `GET /providers/` - Listar prestadores
- `POST /providers/` - Criar prestador
- `GET /providers/{id}/` - Detalhe do prestador
- `PUT /providers/{id}/` - Atualizar prestador
- `DELETE /providers/{id}/` - Excluir prestador

### Payrolls (Folhas de Pagamento)

- `GET /payrolls/` - Listar folhas
- **`POST /payrolls/calculate/`** - Criar folha (com cálculo automático)
- `GET /payrolls/{id}/` - Detalhe da folha (com itens)
- `POST /payrolls/{id}/close/` - Fechar folha
- `POST /payrolls/{id}/mark-paid/` - Marcar como paga
- `PUT /payrolls/{id}/recalculate/` - Recalcular folha DRAFT
- `POST /payrolls/{id}/reopen/` - Reabrir folha fechada
- `DELETE /payrolls/{id}/` - Excluir folha DRAFT

### Filtros

Todos os endpoints de listagem suportam filtros via query parameters:

```
GET /payrolls/?status=DRAFT
GET /payrolls/?reference_month=01/2026
GET /payrolls/?provider=1
```

---

## 📚 Benefícios da Documentação Swagger

✅ Fórmulas de cálculo sempre visíveis  
✅ Exemplos práticos em cada endpoint  
✅ Interface para testar sem Postman  
✅ Validação de campos em tempo real  
✅ Exportável para outras ferramentas  
✅ Atualização automática com o código
