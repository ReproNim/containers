def pytest_configure(config):  # type: ignore[no-untyped-def]
    config.addinivalue_line("markers", "ai_generated: test written with AI assistance")
