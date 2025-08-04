## Project Code Analysis

### `send-claude-message.sh`

This shell script is responsible for sending messages to a specific tmux window. It takes the target `session:window` and the `message` as arguments. It uses `tmux send-keys` to input the message into the specified window and then sends an `Enter` key to submit it. This script is a direct interface for agent communication within the tmux environment.

### `tmux_utils.py`

This Python module provides a comprehensive set of utilities for interacting with Tmux. Key functionalities include:

- `get_tmux_sessions()`: Retrieves a list of all active tmux sessions and their windows.
- `capture_window_content()`: Safely captures the last N lines of content from a specified tmux window.
- `send_keys_to_window()`: Sends arbitrary key presses to a tmux window.
- `send_command_to_window()`: Sends a command to a tmux window, automatically appending an `Enter` key press.
- `get_all_windows_status()`: Gathers detailed status information for all windows across all sessions.
- `create_monitoring_snapshot()`: Formats the tmux status into a human-readable snapshot, likely for LLM consumption.

### LLM Integration Points

Based on the development plan and code analysis, the primary integration point for LLMs is currently `send-claude-message.sh`. The plan proposes replacing this direct Claude API interaction with a modular system. The `tmux_utils.py` module will likely remain a core component for managing the tmux environment, but the actual LLM communication logic will be abstracted.

The proposed `llm_handler.py` module will be crucial for centralizing LLM communication, allowing the system to switch between different LLMs (Gemini, Qwen, LiteLLM) based on a configuration. The existing shell scripts will need to be refactored to call this new Python module instead of directly interacting with the Claude API or hardcoding LLM-specific logic.

