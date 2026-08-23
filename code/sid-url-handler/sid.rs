use anyhow::{bail, Context, Result};
use std::collections::HashMap;
use url::Url;

#[derive(Debug)]
struct Intent {
    action: String,
    params: HashMap<String, String>,
}

fn parse_intent(raw: &str) -> Result<Intent> {
    let url = Url::parse(raw).context("invalid Sid URL")?;

    if url.scheme() != "sid" {
        bail!("unsupported URL scheme: {}", url.scheme());
    }

    let action = url
        .host_str()
        .context("Sid URL is missing an action")?
        .to_owned();

    if !matches!(action.as_str(), "task" | "review") {
        bail!("unsupported Sid action: {action}");
    }

    let params = url
        .query_pairs()
        .map(|(key, value)| (key.into_owned(), value.into_owned()))
        .collect::<HashMap<_, _>>();

    validate_params(&action, &params)?;

    Ok(Intent { action, params })
}

fn validate_params(action: &str, params: &HashMap<String, String>) -> Result<()> {
    if !params.contains_key("repo") {
        bail!("missing required parameter: repo");
    }

    match action {
        "task" => {
            if !params.contains_key("issue") {
                bail!("task requires an issue parameter");
            }
        }

        "review" => {
            if !params.contains_key("pr") {
                bail!("review requires a pr parameter");
            }
        }

        _ => unreachable!(),
    }

    Ok(())
}

fn main() -> Result<()> {
    let raw_url = std::env::args().nth(1).context("usage: sid <sid://...>")?;

    let intent = parse_intent(&raw_url)?;

    println!("Action: {}", intent.action);

    for (key, value) in &intent.params {
        println!("{key}: {value}");
    }

    Ok(())
}
