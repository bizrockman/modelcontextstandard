from __future__ import annotations

"""HTTP‑based reference driver for MCS (extended).

Features:
* Fetches a spec via HTTP(S) (global or per‑call headers)
* Executes structured REST calls (GET/POST)
* Supports common HTTP concerns at **init** time:
  - proxy (http/https) with optional user/password
  - Basic‑Auth header generation
  - custom default headers
  - SSL verification toggle

The driver exposes a single private helper ``_do_request`` so that
``get_function_description`` *and* ``process_llm_response`` share the same
connection logic.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import base64
import requests
import json
import logging
import re

from urllib.parse import urljoin, urlparse
from drivers import MCSDriver


class HTTPRESTDriver(MCSDriver):
    """Fetch spec over HTTP and perform REST calls."""

    def __init__(
        self,
        urls: list[str],
        *,
        reduced_spec: bool = False,
        default_headers: Optional[dict[str, str]] = None,
        proxy_url: str | None = None,
        proxy_port: int | None = None,
        proxy_user: str | None = None,
        proxy_password: str | None = None,
        basic_user: str | None = None,
        basic_password: str | None = None,
        verify_ssl: bool = True,
    ) -> None:
        self.function_desc_urls = urls
        self.reduced_spec = reduced_spec
        self.default_headers: dict[str, str] = default_headers or {}
        self.verify_ssl = verify_ssl

        # configure proxies if provided
        if proxy_url and proxy_port:
            auth_segment = (
                f"{proxy_user}:{proxy_password}@" if proxy_user and proxy_password else ""
            )
            proxy_base = f"{proxy_url}:{proxy_port}"
            full_proxy = f"http://{auth_segment}{proxy_base}"
            self.proxies = {"http": full_proxy, "https": full_proxy}
        else:
            self.proxies: dict[str, str] | None = None

        # basic auth header if needed
        if basic_user and basic_password:
            token = base64.b64encode(f"{basic_user}:{basic_password}".encode()).decode()
            self.default_headers.setdefault("Authorization", f"Basic {token}")

    # ------------------------------------------------------------------
    # internal helper
    # ------------------------------------------------------------------

    def _do_request(
        self,
        method: str,
        url: str,
        *,
        params: Dict[str, Any] | None = None,
        json_body: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> str:
        """Wrapper around requests with shared config."""
        merged_headers = {**self.default_headers, **(headers or {})}
        resp = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json_body,
            headers=merged_headers,
            timeout=15,
            verify=self.verify_ssl,
            proxies=self.proxies,
        )
        resp.raise_for_status()
        return resp.text

    def _reduce_spec(self, spec_text: str) -> str:
        """Strip components and 4xx/5xx validation responses to keep spec small."""
        try:
            import json

            spec = json.loads(spec_text)
        except Exception:
            return spec_text  # not JSON? just return

        # Remove components
        spec.pop("components", None)

        # Optionally prune 4xx/5xx responses
        for path_item in spec.get("paths", {}).values():
            for op in path_item.values():
                if not isinstance(op, dict):
                    continue
                responses = op.get("responses", {})
                # keep only 2xx/3xx
                for code in list(responses):
                    if not str(code).startswith("2") and not str(code).startswith("3"):
                        responses.pop(code, None)
        return json.dumps(spec)

    def get_function_description(self, **kwargs: Any) -> str:  # noqa: D401
        """Fetch the spec and optionally strip unnecessary parts."""
        # Maybe we can also make the funktion a named dict that the LLM can understand more easily
        url = self.function_desc_urls[0]
        headers = kwargs.get("headers")
        spec_text = self._do_request("GET", url, headers=headers)
        if self.reduced_spec:
            spec_text = self._reduce_spec(spec_text)
        return spec_text

    def get_driver_system_message(self) -> str:
        # TODO Improvment needed for more server that the LLM should use.
        system_message = (
            "You are a helpful assistant with access to these tools:\n\n"
            f"{self.get_function_description()}\n"
            "Choose the appropriate tool based on the user's question. "
            "If no tool is needed, reply directly.\n\n"
            "IMPORTANT: When you need to use a tool, you must ONLY respond with "
            "the exact JSON object format below, nothing else:\n"
            "{\n"
            '    "path": "path-name",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "}\n\n"
            "After receiving a tool's response:\n"
            "1. Transform the raw data into a natural, conversational response\n"
            "2. Keep responses concise but informative\n"
            "3. Focus on the most relevant information\n"
            "4. Use appropriate context from the user's question\n"
            "5. Avoid simply repeating the raw data\n\n"
            "Please use only the tools that are explicitly defined above."
            "DO NOT try to use the tool, ALWAYS reply with the JSON object format.\n")
        return system_message

    def _extract_json(self, raw: str) -> str | None:
        """
        Return the first JSON object found in `raw`.
        Strips ```json ...``` or ``` ... ``` fences if present.
        """
        # remove common markdown fences
        try:
            if raw.strip().startswith("```"):
                raw = re.sub(r"^```[^\n]*\n", "", raw.strip())  # opening fence
                raw = re.sub(r"\n```$", "", raw)  # closing fence

                # now try to find the first {...} block
                match = re.search(r"\{.*\}", raw, re.S)
                return match.group(0) if match else None
            else:
                return raw
        except Exception as e:
            logging.error(f"Error extracting JSON from response: {e}")
            return raw

    def process_llm_response(self, llm_response: str) -> str:  # noqa: D401
        """
        Take the raw LLM output, execute the requested tool and
        return the textual result.

        Expected JSON from the model:
        {
            "path": "/tools/fibonacci",
            "method": "GET",          # optional, defaults to GET
            "arguments": { "n": 4 },  # mapped to query or JSON body
            "headers":   { ... }      # optional
        }
        """
        # 1. Parse & validate -------------------------------------------------
        try:
            json_block = self._extract_json(llm_response)
            if not json_block:
                return llm_response
            call = json.loads(json_block)
        except json.JSONDecodeError:
            logging.error("Failed to parse LLM response as JSON.")
            print("Failed to parse LLM response as JSON.")
            return llm_response  # not JSON ⇒ treat as normal assistant text

        if not isinstance(call, dict) or "path" not in call:
            return llm_response  # not a structured tool call

        path: str = call["path"]
        method: str = call.get("method", "GET").upper()
        params: dict[str, Any] = call.get("arguments", {}) or {}
        headers: dict[str, str] = call.get("headers", {}) or {}

        logging.info(f"Executing tool: {call.get('path', 'unknown')} ")
        logging.info(f"With arguments: {call.get('arguments', {})} ")

        # 2. Resolve base-URL --------------------------------------------------
        # Use cached base if we already computed it.
        if not hasattr(self, "_base_url"):
            # try servers[0].url first
            try:
                spec_json = json.loads(self.get_function_description())
                base_candidate = spec_json.get("servers", [{}])[0].get("url")
            except Exception:
                base_candidate = None

            if not base_candidate:
                # fall back to scheme://netloc of the spec’s own URL
                parsed = urlparse(self.function_desc_urls[0])
                base_candidate = f"{parsed.scheme}://{parsed.netloc}"

            self._base_url = base_candidate.rstrip("/")

        full_url = urljoin(self._base_url + "/", path.lstrip("/"))

        # 3. Execute -----------------------------------------------------------
        if method == "GET":
            result_text = self._do_request("GET", full_url, params=params, headers=headers)
        else:
            result_text = self._do_request("POST", full_url, json_body=params, headers=headers)

        logging.info(f"Tool response: {result_text}")
        # 4. Return raw text to outer handler (let caller create final response)
        return result_text
