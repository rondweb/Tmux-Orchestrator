# Multi-LLM Integration Guide for Tmux-Orchestrator

This document provides step-by-step instructions on how to integrate the newly developed multi-LLM support files into your existing Tmux-Orchestrator project. By following these steps, you will enable your orchestrator to utilize various Large Language Models (LLMs) such as LiteLLM, Gemini, Qwen, and Claude.

## 1. Overview of New and Modified Files

During the multi-LLM conversion, the following files were created or significantly modified:

*   **`llm_handler.py` (New)**: This Python module acts as the core abstraction layer for all LLM communication. It contains the logic for interacting with different LLM APIs and routes requests based on your configuration.

*   **`config.yaml` (New)**: This YAML file centralizes all LLM-related settings. You will use this file to specify which LLM to use, its model name, API key (or environment variable reference), and any other relevant parameters.

*   **`send-claude-message.sh` (Modified)**: The original script for sending messages to Claude agents has been updated. It no longer contains direct Claude API calls but instead leverages `llm_handler.py` to communicate with the configured LLM. This makes the script LLM-agnostic.

*   **`schedule_with_note.sh` (Modified)**: This script, used for scheduling check-ins, has been updated to correctly reference the `llm_handler.py` and ensure dynamic pathing.

*   **`README.md` (Modified)**: The main project documentation has been updated to reflect the new multi-LLM capabilities, including instructions on how to configure and use them.

## 2. Integration Steps

Follow these steps to integrate the new multi-LLM functionality into your Tmux-Orchestrator project.

### Step 2.1: Place New Files

Copy the new `llm_handler.py` and `config.yaml` files into the root directory of your `Tmux-Orchestrator` project. This is the same directory where `README.md`, `send-claude-message.sh`, and `tmux_utils.py` are located.

```bash
cp /path/to/downloaded/llm_handler.py /path/to/your/Tmux-Orchestrator/
cp /path/to/downloaded/config.yaml /path/to/your/Tmux-Orchestrator/
```

### Step 2.2: Update Existing Scripts

You need to replace the content of your existing `send-claude-message.sh` and `schedule_with_note.sh` with the updated versions. It is highly recommended to back up your original files before proceeding.

**Option A: Manual Replacement (Recommended for clarity)**

1.  Open your existing `send-claude-message.sh` file in a text editor.
2.  Replace its entire content with the content from the updated `send-claude-message.sh` (which was provided in the previous task).
3.  Do the same for `schedule_with_note.sh`.

**Option B: Using `cp` command (if you have the updated files locally)**

```bash
cp /path/to/downloaded/send-claude-message.sh /path/to/your/Tmux-Orchestrator/
cp /path/to/downloaded/schedule_with_note.sh /path/to/your/Tmux-Orchestrator/
```

### Step 2.3: Install Required Python Packages

The `llm_handler.py` module relies on several Python libraries to interact with different LLMs. You need to install these in your Python environment. Navigate to your `Tmux-Orchestrator` project directory and run the following command:

```bash
pip install litellm google-generativeai anthropic PyYAML requests
```

### Step 2.4: Configure Your LLM

Open the `config.yaml` file you copied in Step 2.1 using a text editor. You need to configure your preferred LLM and provide your API key.

An example `config.yaml` looks like this:

```yaml
active_model: litellm
api_key: YOUR_API_KEY # Replace with your actual API key or set as environment variable
model_name: gpt-3.5-turbo
# base_url: https://api.example.com/v1 # Optional: for custom API endpoints
```

**Important Considerations for `config.yaml`:**

*   **`active_model`**: Set this to your desired LLM. Supported values are `litellm`, `gemini`, `qwen`, or `claude`.
    *   `litellm` is highly recommended as it provides a unified interface for many LLMs, reducing future integration effort.
*   **`api_key`**: **For security, it is strongly recommended to set your API key as an environment variable** (e.g., `export LLM_API_KEY="your_actual_api_key"` in your shell profile like `.bashrc` or `.zshrc`). If you choose to put it directly in `config.yaml`, replace `YOUR_API_KEY` with your actual key.
*   **`model_name`**: Specify the exact model name you wish to use (e.g., `gpt-3.5-turbo` for LiteLLM, `gemini-1.5-pro` for Gemini, `qwen-turbo` for Qwen, `claude-3-opus-20240229` for Claude).
*   **`base_url`**: Only necessary if your LLM provider requires a custom API endpoint URL.

### Step 2.5: Update `README.md` (Optional but Recommended)

While not strictly necessary for functionality, it is highly recommended to update your project's `README.md` file to reflect the new multi-LLM capabilities. This will help you and other users understand the new configuration options and how to interact with the updated orchestrator. The updated `README.md` was provided in the previous task.

## 3. Verifying the Integration

After completing the integration steps, you can verify that your Tmux-Orchestrator is now using the multi-LLM setup:

1.  **Set your API Key Environment Variable**: If you chose to use an environment variable for your API key, ensure it's set in your shell session before running the orchestrator.
    ```bash
    export LLM_API_KEY="your_actual_api_key_here"
    ```
2.  **Run a Test Command**: Try running a command that uses the `send-claude-message.sh` (now `send-llm-message.sh` functionally) script. For example, if you have a tmux session named `my-project` with a window `0`:
    ```bash
    ./send-claude-message.sh my-project:0 "Hello LLM, what is the capital of France?"
    ```
    You should see the response from your configured LLM appearing in the specified tmux window.

3.  **Check `config.yaml`**: Ensure that the `active_model` and `model_name` in your `config.yaml` are correctly picked up by the `llm_handler.py`.

## 4. Troubleshooting

*   **`Error: API key not configured`**: Ensure your `api_key` is correctly set in `config.yaml` or as an environment variable (`LLM_API_KEY`).
*   **`ImportError`**: If you encounter `ImportError` messages, double-check that you have installed all required Python packages (`pip install litellm google-generativeai anthropic PyYAML requests`).
*   **Incorrect LLM Response**: Verify your `config.yaml` settings (`active_model`, `model_name`) and ensure your API key is valid for the chosen LLM.
*   **Script not executable**: If you get a 


permission denied` error when running the shell scripts, make sure they are executable:
    ```bash
    chmod +x send-claude-message.sh
    chmod +x schedule_with_note.sh
    ```

By following this guide, you should be able to successfully integrate multi-LLM support into your Tmux-Orchestrator project, enhancing its capabilities and flexibility.


