# utils-test

Test data and reusable non-specific test code

## fixtures

Fixtures allow us to reuse similiar code between many tests.
Read all about it [here](https://docs.pytest.org/en/latest/fixture.html)

### Indexd

```text
--------- fixtures defined from cdisutilstest.code.conftest ---
indexd_server
    Starts the indexd server, and cleans up its mess.
    Most tests will use the client which stems from this
    server fixture.
    Runs once per test session.
indexd_client
    Returns a IndexClient. This will delete any documents,
    aliases, or users made by this
    client after the test has completed.
    Currently the default user is the admin user
    Runs once per test.
```
