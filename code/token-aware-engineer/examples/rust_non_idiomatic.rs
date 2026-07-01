use std::collections::HashMap;

#[derive(Debug)]
struct Order {
    customer_id: String,
    quantity: u32,
    unit_price: f64,
}

fn is_valid_order(order: &Order) -> bool {
    if order.customer_id.is_empty() {
        return false;
    }

    if order.quantity == 0 {
        return false;
    }

    if order.unit_price <= 0.0 {
        return false;
    }

    true
}

fn customer_totals(orders: &[Order]) -> HashMap<String, f64> {
    let mut totals = HashMap::new();

    for order in orders {
        if !is_valid_order(order) {
            continue;
        }

        let current_total = totals.get(&order.customer_id).copied().unwrap_or(0.0);

        let updated_total = current_total + order.quantity as f64 * order.unit_price;

        totals.insert(order.customer_id.clone(), updated_total);
    }

    totals
}
