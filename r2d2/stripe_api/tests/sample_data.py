STRIPE_TEST_ORDER_RESPONSE = {
    "data": [{
      "amount": 70,
      "amount_returned": "null",
      "application": "null",
      "application_fee": "null",
      "charge": "null",
      "created": 1488227274,
      "currency": "usd",
      "customer": "null",
      "email": "fredbuyyers@yahoo.com",
      "id": "or_19rv66Bm6CxpShfN1YI56AHH",
      "items": [
        {
          "amount": 70,
          "currency": "usd",
          "description": "Flannel Scarf",
          "object": "order_item",
          "parent": "000003",
          "quantity": 1,
          "type": "sku"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Taxes (included)",
          "object": "order_item",
          "parent": "null",
          "quantity": "null",
          "type": "tax"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Free shipping",
          "object": "order_item",
          "parent": "ship_free-shipping",
          "quantity": "null",
          "type": "shipping"
        }
      ],
      "livemode": "false",
      "metadata": {},
      "object": "order",
      "returns": {
        "data": [],
        "has_more": "false",
        "object": "list",
        "total_count": 0,
        "url": "/v1/order_returns?order=or_19rv66Bm6CxpShfN1YI56AHH"
      },
      "selected_shipping_method": "ship_free-shipping",
      "shipping": {
        "address": {
          "city": "Springfield",
          "country": "USA",
          "line1": "103 Fake Ave",
          "line2": "null",
          "postal_code": "94000",
          "state": "CA"
        },
        "carrier": "null",
        "name": "Mr. Fred Buyyers",
        "phone": "null",
        "tracking_number": "null"
      },
      "shipping_methods": [
        {
          "amount": 0,
          "currency": "usd",
          "delivery_estimate": "null",
          "description": "Free shipping",
          "id": "ship_free-shipping"
        }
      ],
      "status": "created",
      "status_transitions": "null",
      "updated": 1488227274
    }, {
      "amount": 260,
      "amount_returned": "null",
      "application": "null",
      "application_fee": "null",
      "charge": "null",
      "created": 1488227255,
      "currency": "usd",
      "customer": "null",
      "email": "fredbuyyers@yahoo.com",
      "id": "or_19rv5nBm6CxpShfNoi7xJlt8",
      "items": [
        {
          "amount": 180,
          "currency": "usd",
          "description": "Scarf Pouch",
          "object": "order_item",
          "parent": "000001",
          "quantity": 2,
          "type": "sku"
        },
        {
          "amount": 80,
          "currency": "usd",
          "description": "Flannel clasp",
          "object": "order_item",
          "parent": "000002",
          "quantity": 1,
          "type": "sku"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Taxes (included)",
          "object": "order_item",
          "parent": "null",
          "quantity": "null",
          "type": "tax"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Free shipping",
          "object": "order_item",
          "parent": "ship_free-shipping",
          "quantity": "null",
          "type": "shipping"
        }
      ],
      "livemode": "false",
      "metadata": {},
      "object": "order",
      "returns": {
        "data": [],
        "has_more": "false",
        "object": "list",
        "total_count": 0,
        "url": "/v1/order_returns?order=or_19rv5nBm6CxpShfNoi7xJlt8"
      },
      "selected_shipping_method": "ship_free-shipping",
      "shipping": {
        "address": {
          "city": "Springfield",
          "country": "USA",
          "line1": "103 Fake Ave",
          "line2": "null",
          "postal_code": "94000",
          "state": "CA"
        },
        "carrier": "null",
        "name": "Mr. Fred Buyyers",
        "phone": "null",
        "tracking_number": "null"
      },
      "shipping_methods": [
        {
          "amount": 0,
          "currency": "usd",
          "delivery_estimate": "null",
          "description": "Free shipping",
          "id": "ship_free-shipping"
        }
      ],
      "status": "created",
      "status_transitions": "null",
      "updated": 1488227255
    }, {
      "amount": 70,
      "amount_returned": "null",
      "application": "null",
      "application_fee": "null",
      "charge": "null",
      "created": 1488226187,
      "currency": "usd",
      "customer": "null",
      "email": "lily.thompson@example.com",
      "id": "or_19ruoZBm6CxpShfNxiR9eu7Y",
      "items": [
        {
          "amount": 70,
          "currency": "usd",
          "description": "Flannel Scarf",
          "object": "order_item",
          "parent": "000003",
          "quantity": 1,
          "type": "sku"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Taxes (included)",
          "object": "order_item",
          "parent": "null",
          "quantity": "null",
          "type": "tax"
        },
        {
          "amount": 0,
          "currency": "usd",
          "description": "Free shipping",
          "object": "order_item",
          "parent": "ship_free-shipping",
          "quantity": "null",
          "type": "shipping"
        }
      ],
      "livemode": "false",
      "metadata": {},
      "object": "order",
      "returns": {
        "data": [],
        "has_more": "false",
        "object": "list",
        "total_count": 0,
        "url": "/v1/order_returns?order=or_19ruoZBm6CxpShfNxiR9eu7Y"
      },
      "selected_shipping_method": "ship_free-shipping",
      "shipping": {
        "address": {
          "city": "San Francisco",
          "country": "US",
          "line1": "1234 Main Street",
          "line2": "null",
          "postal_code": "94111",
          "state": "CA"
        },
        "carrier": "null",
        "name": "Lily Thompson",
        "phone": "null",
        "tracking_number": "null"
      },
      "shipping_methods": [
        {
          "amount": 0,
          "currency": "usd",
          "delivery_estimate": "null",
          "description": "Free shipping",
          "id": "ship_free-shipping"
        }
      ],
      "status": "created",
      "status_transitions": "null",
      "updated": 1488226187
    }],
    "has_more": "false",
    "object": "list",
    "url": "/v1/orders"
}
