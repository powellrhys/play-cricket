# Import dependencies
from backend.functions.logging_functions import log_function_use
import logging

def test_log_function_use_logs_messages(caplog):
    """
    Test that the `log_function_use` decorator correctly logs messages
    when a decorated function is executed successfully.

    Args:
        caplog (pytest.LogCaptureFixture): Pytest fixture used to capture log output.
    """
    # Arrange
    logger = logging.getLogger("test_logger")

    # Define mock function
    @log_function_use(logger)
    def add(a, b):
        return a + b

    # Act
    with caplog.at_level(logging.INFO):
        result = add(2, 3)

    # Assert
    assert result == 5

    # Verify log messages
    log_messages = [record.message for record in caplog.records]
    assert any("executed successfully" in msg for msg in log_messages)
