/// The pure Rust result type used by the calculation engine.
#[derive(Debug, Clone, PartialEq)]
pub struct Summary {
    pub count: usize,
    pub sum: f64,
    pub mean: f64,
    pub minimum: f64,
    pub maximum: f64,
}

/// Errors produced by the Rust calculation engine.
#[derive(Debug, Clone, PartialEq)]
pub enum SummaryError {
    EmptyInput,
    NonFiniteValue { index: usize, value: f64 },
}

/// Calculate basic statistics without depending on Python or PyO3.
pub fn calculate_summary(values: &[f64]) -> Result<Summary, SummaryError> {
    if values.is_empty() {
        return Err(SummaryError::EmptyInput);
    }

    for (index, value) in values.iter().copied().enumerate() {
        if !value.is_finite() {
            return Err(SummaryError::NonFiniteValue { index, value });
        }
    }

    let mut sum = 0.0;
    let mut minimum = values[0];
    let mut maximum = values[0];

    for value in values.iter().copied() {
        sum += value;
        minimum = minimum.min(value);
        maximum = maximum.max(value);
    }

    Ok(Summary {
        count: values.len(),
        sum,
        mean: sum / values.len() as f64,
        minimum,
        maximum,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calculates_summary() {
        let result = calculate_summary(&[10.0, 20.0, 30.0])
            .expect("valid values should produce a summary");

        assert_eq!(result.count, 3);
        assert_eq!(result.sum, 60.0);
        assert_eq!(result.mean, 20.0);
        assert_eq!(result.minimum, 10.0);
        assert_eq!(result.maximum, 30.0);
    }

    #[test]
    fn rejects_empty_input() {
        assert_eq!(calculate_summary(&[]), Err(SummaryError::EmptyInput));
    }

    #[test]
    fn rejects_non_finite_values() {
        let result = calculate_summary(&[10.0, f64::NAN]);

        assert!(matches!(
            result,
            Err(SummaryError::NonFiniteValue { index: 1, .. })
        ));
    }
}
