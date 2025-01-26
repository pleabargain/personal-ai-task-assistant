### Personal AI Task Assistant

![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.14-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37.0-green)
![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)

The **Personal AI Task Assistant** is an interactive AI tool designed to assist with task automation, project management, and decision-making. This version has been modified to run locally using Ollama instead of Anthropic's Claude. The assistant leverages natural language processing to understand user inputs, execute tasks with integrated tools, and provide detailed updates and visualizations of progress.

**Note**: This is primarily a demonstration project showcasing the architecture and potential of AI task automation. It does not have actual integration with calendars, email systems, or personal goals - these are shown as examples of what could be implemented with proper API integrations.

This is a fork of the original project, modified to use Ollama locally instead of Anthropic's Claude. Special thanks to the original author for creating this excellent foundation for exploring AI task automation patterns.


![Workflow Graph](assets/graph.png)

## Key Features

The project operates through a workflow consisting of the following key nodes:

1. **Planner Node**:
   - Analyzes user inputs to develop a step-by-step plan for task execution.
   - Breaks down complex tasks into manageable steps, determining the most efficient path forward.

2. **Task Executor Node**:
   - Executes the tasks outlined in the plan using integrated tools.
   - Utilizes external APIs and systems, such as sending emails, scheduling events, or performing web searches.

3. **Project Updater Node**:
   - Provides a summary of completed tasks, highlighting progress made.
   - Includes a checklist of completed and pending tasks to maintain an overview of the project's status.

4. **Replanner Node**:
   - Evaluates the current progress and determines if the plan needs to be adjusted.
   - Replans tasks as necessary to ensure optimal task completion, accounting for any new developments or insights.

These nodes work in conjunction to manage and automate a wide variety of tasks, ensuring efficient and effective task management from start to finish.

## Current Capabilities

The Task Executor Node demonstrates the potential for task automation through its architecture. While the current implementation focuses on showcasing the workflow and decision-making process, the following capabilities could be integrated:

### Example Integration Points

1. **Calendar Management**
   - Integration with calendar services (Google Calendar, Outlook, etc.)
   - Meeting scheduling and availability checking
   - Event management and reminders

2. **Contact Management**
   - Contact information storage and retrieval
   - Integration with address books or CRM systems

3. **Communication**
   - Email integration for sending notifications and updates
   - Message drafting and scheduling

4. **Information Retrieval**
   - Web search integration
   - Document search and summarization

The current implementation uses Ollama for local execution, making it easy to experiment with and extend these capabilities. To add real functionality, you would need to:

1. Implement the desired API integrations in the Task Executor
2. Add appropriate authentication and credentials management
3. Update the tools configuration to include the new capabilities

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/personal-ai-task-assistant
    cd personal-ai-task-assistant
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure your environment, including any necessary API credentials for integrated tools.

## Usage

1. Run the `app.py` file to launch the Streamlit application:
    ```bash
    streamlit run src/app.py
    ```

2. Access the Streamlit app in your web browser and select the desired AI model.

3. Enter your task or question in the input field and click "Get Assistance."

4. The assistant will generate a task plan, execute the tasks, provide updates, and allow for replanning if needed.

## Example

Input: "Analyze the project structure and create a task list for implementing calendar integration."

Output:
- The assistant breaks down the task into manageable steps
- Provides a detailed plan for implementing calendar functionality
- Shows a project update with a checklist of required tasks
- Demonstrates the planning and replanning capabilities

This example showcases the assistant's ability to analyze tasks and create structured plans, even though the actual calendar integration would need to be implemented separately.

## Contributing

Contributions are welcome! If you'd like to suggest improvements or add new features, please submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---
