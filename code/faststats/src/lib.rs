mod summary;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::summary::{
    Summary as DomainSummary,
    SummaryError,
    calculate_summary,
};

/// A Python-visible result object backed by a Rust struct.
#[pyclass(module = "faststats._core", frozen)]
#[derive(Debug, Clone)]
struct Summary {
    #[pyo3(get)]
    count: usize,

    #[pyo3(get)]
    sum: f64,

    #[pyo3(get)]
    mean: f64,

    #[pyo3(get)]
    minimum: f64,

    #[pyo3(get)]
    maximum: f64,
}

impl From<DomainSummary> for Summary {
    fn from(value: DomainSummary) -> Self {
        Self {
            count: value.count,
            sum: value.sum,
            mean: value.mean,
            minimum: value.minimum,
            maximum: value.maximum,
        }
    }
}

#[pymethods]
impl Summary {
    fn __repr__(&self) -> String {
        format!(
            "Summary(count={}, sum={}, mean={}, minimum={}, maximum={})",
            self.count,
            self.sum,
            self.mean,
            self.minimum,
            self.maximum,
        )
    }
}

/// Python-facing wrapper around the pure Rust calculation function.
#[pyfunction]
fn summarize(values: Vec<f64>) -> PyResult<Summary> {
    calculate_summary(&values)
        .map(Summary::from)
        .map_err(summary_error_to_python)
}

/// Convert domain-specific Rust errors into familiar Python exceptions.
fn summary_error_to_python(error: SummaryError) -> PyErr {
    match error {
        SummaryError::EmptyInput => {
            PyValueError::new_err("values must contain at least one number")
        }
        SummaryError::NonFiniteValue { index, value } => PyValueError::new_err(format!(
            "values[{index}] must be finite, received {value}"
        )),
    }
}

/// Native module initialiser called when Python imports `faststats._core`.
#[pymodule]
fn _core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Summary>()?;
    module.add_function(wrap_pyfunction!(summarize, module)?)?;
    Ok(())
}
