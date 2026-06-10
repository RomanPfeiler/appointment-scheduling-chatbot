FROM python:3.11-slim

# HF Spaces requires a non-root user with uid 1000
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install dependencies before copying app code (better layer caching)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app files — .env is intentionally excluded (API key comes from HF Secrets).
# Everything below is on the module-load import graph of `import app`:
#   app.py builds the LangGraph at import -> orchestrator/.nodes.annotate imports
#   nlp.factory (NLP Arm 1) -> nlp/ is needed. The local GGUF (*.gguf) is
#   gitignored and never in the build context, so copying nlp/ does NOT bring the
#   model. public/ holds the custom CSS + avatar referenced by config.toml.
# NOTE: evaluation/ is deliberately NOT copied — the ad-hoc recorder is disabled
# on HF (ephemeral FS), so evaluation.adhoc is never imported on the deployed
# boot path. This keeps the eval data/results off the public Space and the image
# lean. (Local dev still uses it via the lazy, IS_HF_SPACE-gated import in app.py.)
COPY --chown=user app.py chainlit.md ./
COPY --chown=user .chainlit/ ./.chainlit/
COPY --chown=user public/ ./public/
COPY --chown=user orchestrator/ ./orchestrator/
COPY --chown=user mcp_server/ ./mcp_server/
COPY --chown=user nlp/ ./nlp/
# mcp_client/ is NOT copied (2026-06-10): the app talks to the MCP server via
# orchestrator/mcp_bridge.py (the mcp SDK directly); mcp_client/ is only the
# standalone demo client for local manual testing.

EXPOSE 7860

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860", "-h"]
