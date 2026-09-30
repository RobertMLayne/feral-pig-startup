"""Optional JavaScript-rendered capture with the same exact-host boundary."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class RenderedPage:
    html: bytes
    screenshot: bytes
    url: str
    pdf: bytes = b""
    selected_html: bytes = b""
    selector: str = ""


class PlaywrightRenderer:
    def capture(self, url: str, allowed_hosts: set[str], timeout_ms: int = 30000, *, render_pdf: bool = False, content_selector: str = "") -> RenderedPage:
        launch_options = browser_launch_options()
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError as exc:
            raise RuntimeError("rendered capture requires the optional Playwright package and Chromium browser, or an installed Chrome/Edge selected with REFERENCE_SUITE_BROWSER") from exc
        initial = urlparse(url)
        if initial.scheme != "https" or initial.hostname not in allowed_hosts:
            raise ValueError("rendered URL is outside the approved HTTPS hosts")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_options)
            try:
                context = browser.new_context(service_workers="block", accept_downloads=False)
                page = context.new_page()

                def route_handler(route):
                    target = urlparse(route.request.url)
                    if target.scheme == "https" and target.hostname in allowed_hosts:
                        route.continue_()
                    else:
                        route.abort()

                page.route("**/*", route_handler)
                page.route_web_socket("**/*", lambda socket: socket.close())
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(1000)
                final = urlparse(page.url)
                if final.scheme != "https" or final.hostname not in allowed_hosts:
                    raise ValueError("rendered page navigated outside approved HTTPS hosts")
                selected_html = b""
                selected_selector = ""
                candidates = [content_selector] if content_selector else ["main", "article", "[role='main']", "#content", ".content"]
                best_length = 0
                for candidate in candidates:
                    try:
                        locator = page.locator(candidate).first
                        if locator.count():
                            content = locator.inner_text(timeout=3000)
                            if len(content.strip()) > best_length:
                                selected_html = locator.evaluate("element => element.outerHTML").encode("utf-8")
                                selected_selector = candidate
                                best_length = len(content.strip())
                    except Exception:
                        if content_selector:
                            raise ValueError("content selector did not match a readable element")
                if content_selector and not selected_html:
                    raise ValueError("content selector did not match a readable element")
                result = RenderedPage(page.content().encode("utf-8"), page.screenshot(full_page=True), page.url, page.pdf(print_background=True) if render_pdf else b"", selected_html, selected_selector)
                context.close()
                return result
            finally:
                browser.close()


def browser_launch_options() -> dict:
    """Use bundled Chromium by default or an explicitly selected local browser."""
    options = {"headless": True}
    browser_value = os.environ.get("REFERENCE_SUITE_BROWSER", "").strip()
    if browser_value:
        browser_path = Path(browser_value).expanduser()
        if not browser_path.is_absolute() or not browser_path.is_file():
            raise ValueError("REFERENCE_SUITE_BROWSER must be an absolute path to an existing Chrome/Edge executable")
        if not os.access(browser_path, os.X_OK):
            raise ValueError("REFERENCE_SUITE_BROWSER is not executable")
        options["executable_path"] = str(browser_path.resolve())
    return options
