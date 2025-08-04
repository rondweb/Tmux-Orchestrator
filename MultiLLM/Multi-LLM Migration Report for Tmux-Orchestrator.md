# Multi-LLM Migration Report for Tmux-Orchestrator

## 1. Introduction

This report outlines a comprehensive plan for refactoring the Tmux-Orchestrator codebase to support multiple Large Language Models (LLMs). The primary objective is to transition from direct, hardcoded Claude API calls to a modular and configurable system capable of integrating various LLMs, such as Gemini and Qwen, either directly via their APIs or through an abstraction layer like LiteLLM. This migration will enhance the flexibility, scalability, and future-proofing of the Tmux-Orchestrator, allowing users to leverage different LLM capabilities and cost efficiencies.

## 2. Current Architecture Analysis

The existing Tmux-Orchestrator project, as observed from the GitHub repository [1] and its `README.md` [2], is designed to enable AI agents (specifically Claude) to work autonomously within a `tmux` environment. The core concept revolves around a hierarchical agent structure (Orchestrator, Project Managers, Engineers) that communicates and coordinates tasks. The interaction with the Claude LLM is currently tightly coupled within the system.

Key components identified in the current architecture related to LLM interaction include:

*   **`send-claude-message.sh`**: This shell script serves as the primary interface for sending messages to Claude agents operating within specific `tmux` windows. It directly utilizes `tmux send-keys` to input messages and simulate an `Enter` press, effectively acting as a bridge between the orchestrator's logic and the LLM running in a terminal. The script's simplicity means it directly embeds the communication mechanism, making it specific to the current Claude setup.

*   **`tmux_utils.py`**: This Python module provides robust functionalities for managing and interacting with `tmux` sessions and windows. While not directly involved in LLM API calls, it is crucial for the orchestrator's operation, enabling it to:
    *   Retrieve information about `tmux` sessions and windows (`get_tmux_sessions`, `get_window_info`, `get_all_windows_status`).
    *   Capture content from `tmux` windows (`capture_window_content`), which is essential for the LLM to perceive the environment and agent outputs.
    *   Send commands and key presses to `tmux` windows (`send_keys_to_window`, `send_command_to_window`), which `send-claude-message.sh` leverages.
    *   Generate monitoring snapshots (`create_monitoring_snapshot`) that are formatted for LLM consumption, providing context for decision-making.

Currently, the system's reliance on `send-claude-message.sh` for LLM communication means that any change in the LLM provider or its API would necessitate direct modification of this script and potentially other parts of the codebase. This monolithic approach to LLM integration limits flexibility and makes it challenging to incorporate new LLMs or switch between them dynamically. The system's design is heavily optimized for Claude, as evidenced by the script names and the project's initial focus.

## 3. Proposed Multi-LLM Architecture

To achieve multi-LLM support, the proposed architecture introduces an abstraction layer that decouples the orchestrator's core logic from specific LLM implementations. This will involve creating a unified configuration system and a dedicated LLM handling module. The goal is to allow the orchestrator to seamlessly switch between different LLMs based on user preferences or task requirements.

### 3.1 Unified Configuration System

A central `config.yaml` file will be introduced to manage all LLM-related settings. This file will provide a clear and easily modifiable interface for configuring the active LLM and its parameters. The configuration will include:

*   `active_model`: Specifies the LLM to be used (e.g., `gemini`, `qwen`, `litellm`). This will be the primary switch for selecting the LLM.
*   `api_key`: The API key for the selected LLM. For security, this should be loaded from environment variables rather than being hardcoded directly in the configuration file.
*   `model_name`: The specific model variant to be used (e.g., `gemini-1.5-pro`, `qwen-turbo`, or a LiteLLM-supported model name).
*   `base_url`: (Optional) Any custom base URLs for API endpoints, if applicable.
*   Other LLM-specific parameters: Any additional parameters required by a particular LLM's API (e.g., temperature, max tokens, system prompts).

This centralized configuration will simplify LLM management, allowing users to switch LLMs by simply modifying a single file and restarting the orchestrator.

### 3.2 LLM Abstraction Layer (`llm_handler.py`)

A new Python module, `llm_handler.py`, will be developed to serve as the single point of entry for all LLM communication. This module will encapsulate the logic for interacting with different LLM APIs, abstracting away their specific request and response formats. The `llm_handler.py` will contain:

*   **`send_message(agent_name, prompt)` function**: This will be the main function called by the orchestrator and other scripts. It will read the `active_model` from the `config.yaml` and dynamically route the request to the appropriate sub-function responsible for handling that specific LLM.

*   **LLM-specific sub-functions**: For each supported LLM, a dedicated sub-function will be implemented to handle its unique API interactions. Examples include:
    *   `_send_gemini_message(prompt)`: Responsible for formatting the prompt and making API calls to the Gemini API, parsing its response, and returning a standardized output.
    *   `_send_qwen_message(prompt)`: Handles the specific request and response formats for the Qwen API.
    *   `_send_litellm_message(prompt)`: This function will leverage the LiteLLM library to provide a unified interface for a wide range of LLMs. LiteLLM simplifies the process by abstracting various LLM APIs behind a single `completion()` call. This approach is highly recommended as it minimizes the need for implementing individual API integrations for each new LLM, promoting greater flexibility and reducing maintenance overhead.

This abstraction layer ensures that the core orchestrator logic remains independent of the underlying LLM technology. When a new LLM needs to be integrated, only `llm_handler.py` (or the LiteLLM configuration) would require modification, rather than widespread changes across the codebase.

## 4. Refactoring Strategy

The migration to a multi-LLM architecture necessitates refactoring existing scripts to interact with the new `llm_handler.py` module. The primary focus will be on `send-claude-message.sh` and any other scripts that currently embed LLM-specific logic.

### 4.1 Modifying `send-claude-message.sh`

The `send-claude-message.sh` script will be refactored to remove all hardcoded Claude API calls and LLM-specific logic. Instead, it will be modified to invoke the new `llm_handler.py` module. The updated script will:

1.  **Accept `session:window` and `message` as arguments**: Similar to its current functionality, it will still determine the target `tmux` window for communication.
2.  **Call `llm_handler.py`**: It will execute `llm_handler.py` (e.g., `python3 llm_handler.py <agent_name> <prompt>`) with the necessary arguments. The `agent_name` can be derived from the `session:window` information or passed as an additional argument.
3.  **Process LLM response**: The `llm_handler.py` will return the LLM's response, which the shell script can then process. For instance, the response might be echoed back into the `tmux` window or used to trigger subsequent actions.

This refactoring ensures that `send-claude-message.sh` becomes a generic `tmux` communication utility, completely decoupled from the specific LLM being used. The responsibility of interacting with the LLM API shifts entirely to `llm_handler.py`.

### 4.2 Updating Other Scripts and Modules

Any other scripts or Python modules within the Tmux-Orchestrator that currently make direct or indirect calls to the Claude API will need to be identified and updated. These components will be modified to utilize the `llm_handler.py` module for all LLM interactions. This ensures consistency and centralizes LLM communication across the entire codebase.

## 5. Testing and Optimization Considerations

Thorough testing and optimization are critical to ensure the stability, reliability, and performance of the multi-LLM Tmux-Orchestrator. The testing strategy will encompass unit testing, end-to-end testing, and prompt/agent tuning.

### 5.1 Unit Testing

Unit tests will be developed for the `llm_handler.py` module to verify its functionality in isolation. These tests will:

*   **Verify correct routing**: Ensure that `send_message` correctly routes requests to the appropriate LLM-specific sub-function based on the `active_model` configuration.
*   **Validate API request formatting**: Confirm that each LLM-specific sub-function correctly formats requests according to the respective LLM's API specifications.
*   **Test response parsing**: Verify that the module correctly parses responses from different LLMs and returns a standardized output.
*   **Mock API calls**: Utilize mocking frameworks to simulate LLM API responses. This will allow for fast and reliable tests without incurring actual API costs or relying on external network connectivity.

### 5.2 End-to-End Testing

End-to-end testing will involve running the complete Tmux-Orchestrator system with various LLMs configured via `config.yaml`. This will validate the entire workflow, from agent task assignment to LLM interaction and response processing. Key aspects to verify include:

*   **Agent communication**: Ensure that agents can successfully communicate with the configured LLM and receive responses.
*   **Task execution**: Validate that agents can successfully execute a predefined test task from start to finish using different LLMs.
*   **Stability and error handling**: Monitor the system for stability, identify potential error scenarios, and verify that error handling mechanisms are robust.
*   **Performance**: Assess the performance of the orchestrator with different LLMs, noting any significant latency or resource consumption differences.

### 5.3 Prompt and Agent Tuning

LLMs often have different strengths, weaknesses, and optimal prompting strategies. Prompts and agent instructions initially designed for Claude may not yield optimal results with Gemini or Qwen. Therefore, a crucial optimization step will involve tuning prompts and agent behaviors for each new LLM:

*   **Adjusting system messages**: Modify the 


system messages" or "persona" prompts to align with the instruction-following capabilities and nuances of Gemini, Qwen, or other LLMs.
*   **Iterative prompt refinement**: Experiment with different phrasing, examples, and constraints to elicit the desired behavior and output quality from each LLM.
*   **Leveraging LLM-specific features**: Identify and utilize unique features or capabilities offered by each LLM (e.g., specific safety settings, function calling, or multimodal inputs) to enhance agent performance.

This iterative tuning process will ensure that the Tmux-Orchestrator can effectively leverage the strengths of each integrated LLM, leading to improved agent performance and more reliable task execution.

## 6. Documentation and Finalization

Comprehensive documentation is essential for the usability and maintainability of the multi-LLM Tmux-Orchestrator. This phase focuses on updating existing documentation and performing final code cleanup before merging the changes.

### 6.1 Updating the `README.md`

The `README.md` file will be updated to provide clear and concise instructions for users and developers. This will include:

*   **Quick Start Guide**: Step-by-step instructions on how to set up and run the orchestrator with different LLMs.
*   **Configuration Details**: A detailed explanation of the `config.yaml` file, including all available parameters and their purpose.
*   **API Key Management**: Clear guidance on securely setting up environment variables for API keys.
*   **LLM Selection**: Instructions on how to switch between different LLMs and the implications of each choice.
*   **Troubleshooting**: Common issues and their solutions related to multi-LLM setup.

### 6.2 Final Code Cleanup

Before finalizing the migration, a thorough code cleanup will be performed. This includes:

*   **Removing deprecated code**: Eliminating any code specifically tied to the old Claude-only integration that is no longer needed.
*   **Code review**: Ensuring code quality, readability, and adherence to best practices.
*   **Commenting**: Adding or updating comments to explain complex logic or design decisions.
*   **Error handling**: Reviewing and enhancing error handling mechanisms across the codebase.

### 6.3 Version Control and Branch Merging

The entire migration process will be conducted within a dedicated Git branch. Once all development, testing, and documentation updates are complete, the new branch will be merged into the main repository. This ensures a clean and traceable development history.

## 7. Conclusion

The migration of Tmux-Orchestrator to multi-LLM support represents a significant enhancement to its capabilities and flexibility. By introducing a modular architecture with a unified configuration and an LLM abstraction layer, the project will be better positioned to adapt to the evolving landscape of large language models. This will empower users to choose the most suitable LLM for their needs, optimize costs, and leverage diverse AI capabilities within their automated `tmux` environments.

## 8. References

[1] Jedward23/Tmux-Orchestrator. *GitHub*. Available at: [https://github.com/Jedward23/Tmux-Orchestrator](https://github.com/Jedward23/Tmux-Orchestrator)

[2] Jedward23. (2024). *README.md* in Tmux-Orchestrator. *GitHub*. Available at: [https://github.com/Jedward23/Tmux-Orchestrator/blob/main/README.md](https://github.com/Jedward23/Tmux-Orchestrator/blob/main/README.md)



