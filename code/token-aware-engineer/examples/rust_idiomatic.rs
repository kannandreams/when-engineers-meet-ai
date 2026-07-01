use std::collections::HashMap;

#[derive(Debug)]
struct Order {
    customer_id: String,
    quantity: u32,
    unit_price: f64,
}

fn customer_totals(orders: &[Order]) -> HashMap<&str, f64> {
    orders
        .iter()
        .filter(|o| !o.customer_id.is_empty() && o.quantity > 0 && o.unit_price > 0.0)
        .fold(HashMap::new(), |mut totals, o| {
            *totals.entry(&o.customer_id).or_default() += o.quantity as f64 * o.unit_price;

            totals
        })
}
