# Usage Examples - Voice & Text Modes

## Voice Mode Examples

### Example 1: Basic Voice Query
**Spoken:** "Show me all customers from India"

**System Output:**
```
Mic level: 0.156

[VOICE QUERY]
Show me all customers from India

[SQL]
SELECT Customers.customer_id, Customers.first_name, Customers.last_name 
FROM Customers WHERE Customers.country = 'India';

[RESULTS]
{'customer_id': 1, 'first_name': 'Aarav', 'last_name': 'Sharma'}
{'customer_id': 22, 'first_name': 'Priya', 'last_name': 'Iyer'}
{'customer_id': 28, 'first_name': 'Ravi', 'last_name': 'Patel'}
...
```

### Example 2: Aggregation Query
**Spoken:** "How many orders did each customer place?"

**System Output:**
```
[VOICE QUERY]
How many orders did each customer place

[SQL]
SELECT Customers.customer_id, Customers.first_name, Customers.last_name, 
COUNT(Orders.order_id) as order_count
FROM Customers 
JOIN Orders ON Customers.customer_id = Orders.customer_id 
GROUP BY Customers.customer_id;

[RESULTS]
{'customer_id': 1, 'first_name': 'Aarav', 'last_name': 'Sharma', 'order_count': 3}
{'customer_id': 2, 'first_name': 'Emily', 'last_name': 'Clark', 'order_count': 2}
...
```

### Example 3: Complex Filter
**Spoken:** "List customers from USA who bought laptops above 1000 dollars"

**System Output:**
```
[VOICE QUERY]
List customers from USA who bought laptops above 1000 dollars

[SQL]
SELECT DISTINCT Customers.customer_id, Customers.first_name, Customers.last_name
FROM Customers 
JOIN Orders ON Customers.customer_id = Orders.customer_id 
WHERE Customers.country = 'USA' 
AND Orders.item LIKE '%laptop%' 
AND Orders.amount > 1000;

[RESULTS]
{'customer_id': 2, 'first_name': 'Emily', 'last_name': 'Clark'}
{'customer_id': 21, 'first_name': 'Daniel', 'last_name': 'Smith'}
```

### Example 4: HR Schema Query
**Spoken:** "Show employees in the engineering department"

**System Output:**
```
[VOICE QUERY]
Show employees in the engineering department

[SQL]
SELECT Employees.employee_id, Employees.name, Departments.department_name
FROM Employees
JOIN Departments ON Employees.department_id = Departments.department_id
WHERE Departments.department_name = 'Engineering';

[RESULTS]
{'employee_id': 5, 'name': 'John Doe', 'department_name': 'Engineering'}
{'employee_id': 12, 'name': 'Jane Smith', 'department_name': 'Engineering'}
```

## Text API Examples

### Example 5: cURL Request
```bash
curl -X POST http://127.0.0.1:9000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show delivered shipments",
    "role": "ops"
  }'
```

**Response:**
```json
{
  "sql": "SELECT Shippings.shipping_id, Shippings.order_id, Shippings.status_text FROM Shippings WHERE Shippings.status_text = 'Delivered';",
  "results": [
    {"shipping_id": 1, "order_id": 45, "status_text": "Delivered"},
    {"shipping_id": 5, "order_id": 67, "status_text": "Delivered"}
  ]
}
```

### Example 6: Python Client
```python
import requests

url = "http://127.0.0.1:9000/generate_sql"

# First query
response = requests.post(url, json={
    "question": "Show customers who ordered laptops",
    "role": "admin"
})
print(response.json()["sql"])

# Follow-up query (remembers context)
response = requests.post(url, json={
    "question": "Only those from Europe",
    "role": "admin"
})
print(response.json()["sql"])
```

### Example 7: Multi-Schema Routing
```python
# Commerce schema
requests.post(url, json={
    "question": "Total orders by country",
    "role": "admin"
})
# → Uses Customers, Orders tables

# HR schema
requests.post(url, json={
    "question": "Average employee age by department",
    "role": "hr_user"
})
# → Uses Employees, Departments tables
```

## Web UI Examples

### Example 8: Voice Recording
1. Open `http://127.0.0.1:9000`
2. Select role: `admin`
3. Click 🎤 microphone button
4. Speak: "Show customers older than 40"
5. View results in table format

### Example 9: Text Input
1. Type in text box: "List all orders for customer ID 5"
2. Click "Submit"
3. See SQL and results side-by-side

## Role-Based Examples

### Example 10: Sales Role (Limited Access)
```bash
curl -X POST http://127.0.0.1:9000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show customer ages",
    "role": "sales"
  }'
```

**Response:**
```json
{
  "error": "Column 'age' not available for sales role"
}
```

### Example 11: Ops Role (Shipping Focus)
**Voice:** "Show me shipped orders"

**SQL:**
```sql
SELECT Shippings.shipping_id, Shippings.order_id, Shippings.status_text 
FROM Shippings 
WHERE Shippings.status_text = 'Shipped';
```

## Advanced Features

### Example 12: Fuzzy Matching
**Spoken (with typo):** "Show custmers from Indai"

**Normalized to:** "Show customers from India"

**SQL:** (correct query generated despite typos)

### Example 13: Follow-up Queries
**Query 1:** "Show customers who bought laptops"
```sql
SELECT DISTINCT Customers.customer_id, Customers.first_name, Customers.last_name
FROM Customers JOIN Orders ON Customers.customer_id = Orders.customer_id
WHERE Orders.item LIKE '%laptop%';
```

**Query 2:** "Only those from USA"
```sql
SELECT DISTINCT Customers.customer_id, Customers.first_name, Customers.last_name
FROM Customers JOIN Orders ON Customers.customer_id = Orders.customer_id
WHERE Orders.item LIKE '%laptop%' AND Customers.country = 'USA';
```

### Example 14: Chat Mode
**Spoken:** "Hello, how are you?"

**Response:**
```json
{
  "message": "Hello! I'm ready to help you query the database. You can ask about customers, orders, or shipments.",
  "intent": "chat"
}
```

### Example 15: Explain Mode
**Query 1:** (generates SQL)
**Query 2:** "Explain this query"

**Response:**
```json
{
  "message": "This query retrieves customer names by joining the Customers and Orders tables. It filters for items containing 'laptop' and groups results by customer to show unique buyers.",
  "intent": "explain"
}
```

## Error Handling Examples

### Example 16: Invalid SQL (Auto-Retry)
**First Attempt (Invalid):**
```sql
SELECT * FROM customer WHERE country = India;
```

**Error:** Table 'customer' not in schema

**Second Attempt (Fixed):**
```sql
SELECT Customers.customer_id, Customers.first_name, Customers.last_name 
FROM Customers WHERE Customers.country = 'India';
```

### Example 17: Low Confidence Audio
**Scenario:** Background noise, unclear speech

**Output:**
```
Mic level: 0.089
[discarded low-confidence audio]
```

**Solution:** Speak louder or reduce background noise

## Performance Examples

### Example 18: Streaming Voice
```
Mic level: 0.142  # Real-time volume indicator
Mic level: 0.198
Mic level: 0.156

[VOICE QUERY]
...
```

### Example 19: Batch Queries
```python
questions = [
    "Show customers from USA",
    "Show customers from UK",
    "Show customers from India"
]

for q in questions:
    response = requests.post(url, json={"question": q, "role": "admin"})
    print(response.json()["sql"])
```

## ngrok Remote Access

### Example 20: Public API
```bash
# Start ngrok
ngrok http 9000

# Use public URL
curl -X POST https://abc123.ngrok.io/generate_sql \
  -H "Content-Type: application/json" \
  -d '{"question": "Show all customers", "role": "admin"}'
```

### Example 21: Voice Client with Remote Server
Edit `live_asr.py`:
```python
NL_SQL_ENDPOINT = "https://abc123.ngrok.io/generate_sql"
```

Run: `python live_asr.py`

Now your voice client can access the server remotely!

## Database Examples

### Example 22: View Database Contents
```python
from client import execute_sql

# View customers
rows = execute_sql("SELECT * FROM Customers LIMIT 5;")
for row in rows:
    print(row)

# View orders
rows = execute_sql("SELECT * FROM Orders WHERE amount > 1000;")
print(f"Found {len(rows)} orders above $1000")
```

### Example 23: Schema Inspection
```bash
sqlite3 database.sqlite

.schema Customers
.schema Orders
.schema Shippings
```

## Troubleshooting Examples

### Example 24: Debug Voice Pipeline
```python
# In live_asr.py, add logging
print(f"Audio buffer size: {len(buffer)}")
print(f"VAD detected speech: {len(speech) > 0}")
print(f"Transcription confidence: {seg.avg_logprob}")
```

### Example 25: Test Components Individually
```python
# Test database
from client import execute_sql
rows = execute_sql("SELECT COUNT(*) as total FROM Customers;")
print(rows)

# Test LLM
from server_ollama import call_ollama_raw
result = call_ollama_raw("Generate SQL: show customers")
print(result)
```
