SCHEMAS = {
    "commerce": {
        "description": "Customers, orders, and shipping data",
        "tables": {
            "Customers": {
                "columns": {
                    "customer_id": "INTEGER",
                    "first_name": "TEXT",
                    "last_name": "TEXT",
                    "age": "INTEGER",
                    "country": "TEXT",
                }
            },
            "Orders": {
                "columns": {
                    "order_id": "INTEGER",
                    "item": "TEXT",
                    "amount": "INTEGER",
                    "customer_id": "INTEGER",
                }
            },
            "Shippings": {
                "columns": {
                    "shipping_id": "INTEGER",
                    "order_id": "INTEGER",
                    "status_text": "VARCHAR(20)",
                }
            },
        }
    },

    "hr": {
        "description": "Employee and department data",
        "tables": {
            "Employees": {
                "columns": {
                    "employee_id": "INTEGER",
                    "name": "TEXT",
                    "age": "INTEGER",
                    "department_id": "INTEGER",
                }
            },
            "Departments": {
                "columns": {
                    "department_id": "INTEGER",
                    "department_name": "TEXT",
                }
            }
        }
    }
}
