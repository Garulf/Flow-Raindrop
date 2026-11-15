import asyncio

import httpx

import main
from conftest import ITEMS, TOKEN


def run_query(text):
    return [result.to_json() for result in asyncio.run(main.query(text))]


def test_query_without_token_asks_for_settings(settings, api):
    settings["api_token"] = ""
    (result,) = run_query("python")
    assert result["Title"] == "No API token found!"
    assert result["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenSettingDialog"
    assert api.requests == []


def test_empty_query_returns_nothing(api):
    assert run_query("") == []
    assert api.requests == []


def test_query_searches_all_collections_with_token(api):
    run_query("python")
    (request,) = api.requests
    assert request.method == "GET"
    assert str(request.url) == "https://api.raindrop.io/rest/v1/raindrops/0?search=python"
    assert request.headers["Authorization"] == f"Bearer {TOKEN}"


def test_query_results_open_bookmarks_in_api_order(api):
    results = run_query("python")
    assert [r["Title"] for r in results] == [item["title"] for item in ITEMS]
    first, second = results
    assert first["SubTitle"] == ITEMS[0]["excerpt"]
    assert first["IcoPath"] == ITEMS[0]["cover"]
    assert first["ContextData"] == []
    assert first["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenUrl"
    assert first["JsonRPCAction"]["Parameters"][0] == ITEMS[0]["link"]
    assert second["IcoPath"] is None


def test_repeated_query_is_served_from_cache(api, cache_dir):
    run_query("python")
    run_query("python")
    assert len(api.requests) == 1
    assert (cache_dir / "hishel").is_dir()


def test_clear_cache_removes_cached_responses(api, cache_dir):
    run_query("python")
    main.clear_cache()
    assert not cache_dir.exists()
    run_query("python")
    assert len(api.requests) == 2


def test_rejected_token_points_to_settings(api):
    api.status_code = 401
    (result,) = run_query("python")
    assert result["Title"] == "Raindrop.io rejected the API token"
    assert result["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenSettingDialog"


def test_network_error_is_shown_as_result(api):
    api.error = httpx.ConnectError("Name or service not known")
    (result,) = run_query("python")
    assert result["Title"] == "Could not search Raindrop.io"
    assert result["SubTitle"] == "Name or service not known"


def test_context_menu_opens_raindrop_and_clears_cache():
    first, second = [r.to_json() for r in main.context_menu([])]
    assert first["Title"] == "Open Raindrop.io"
    assert first["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenUrl"
    assert first["JsonRPCAction"]["Parameters"][0] == "https://raindrop.io"
    assert second["Title"] == "Clear cached data"
    assert second["JsonRPCAction"]["Method"] == "clear_cache"
    assert second["JsonRPCAction"]["Parameters"] == []


def test_cache_ttl_setting(settings):
    settings["cache_ttl"] = "1 day"
    assert main.cache_ttl() == 86400
    settings["cache_ttl"] = "unknown"
    assert main.cache_ttl() == main.DEFAULT_CACHE_TTL
    del settings["cache_ttl"]
    assert main.cache_ttl() == main.DEFAULT_CACHE_TTL


def test_query_without_cache_ttl_setting(settings, api):
    del settings["cache_ttl"]
    assert [r["Title"] for r in run_query("python")] == [item["title"] for item in ITEMS]


def test_clear_cache_without_cache_is_harmless(cache_dir):
    main.clear_cache()
    main.clear_cache()
    assert not cache_dir.exists()
