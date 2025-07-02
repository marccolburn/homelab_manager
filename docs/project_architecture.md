# Project Architecture

## Overview

Homelab Manager is an API-first lab management system with three main components:

```mermaid
graph TB
    CLI[CLI Client] --> API[Flask Backend API]
    WEB[Web UI] --> API
    API --> CLAB[clab-tools]
    API --> GIT[Git Operations]
    API --> NB[NetBox Integration]
```

## Directory Structure

### Frontend Components Tree

```
src/
├── cli/                    # CLI Client (Python)
│   ├── main.py            # Entry point & command registration
│   ├── client.py          # HTTP API client
│   ├── commands/          # Command implementations
│   │   ├── repo.py       # Repository management commands
│   │   ├── lab.py        # Lab deployment commands (deploy, destroy, status, logs)
│   │   ├── device_config.py # Configuration scenarios
│   │   └── system.py     # System commands (doctor, version, netbox)
│   └── utils/            # CLI utilities
└── web/                  # Web UI (HTML/CSS/JS)
    └── static/
        ├── js/
        │   ├── api.js    # API client functions
        │   ├── app.js    # Main application logic
        │   ├── ui.js     # UI helper functions
        │   └── settings.js # Settings page logic
        ├── css/          # Stylesheets
        ├── index.html    # Main dashboard
        └── settings.html # Settings page
```

### Backend Components Tree

```
src/backend/
├── app.py                 # Flask application & static file serving
├── api/                   # REST API endpoints
│   ├── repos.py          # Repository management endpoints
│   ├── labs.py           # Lab deployment endpoints
│   ├── tasks.py          # Async task tracking endpoints
│   ├── health.py         # Health check endpoints
│   └── settings.py       # Configuration management endpoints
├── core/                  # Business logic modules
│   ├── lab_manager.py    # Main orchestration class
│   ├── git_ops.py        # Git repository operations
│   ├── clab_runner.py    # clab-tools integration & execution
│   └── config.py         # Configuration management
├── integrations/          # External system integrations
│   └── netbox.py         # NetBox IP management
└── utils/                 # Shared utilities
    ├── validators.py     # Input validation
    └── helpers.py        # Common helper functions
```

## Code Flow Diagrams

### CLI Command Flow

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as labctl CLI
    participant C as HTTP Client
    participant API as Flask API
    participant LM as LabManager
    participant GT as External Tools

    U->>CLI: labctl deploy bgp-lab
    CLI->>C: create HTTP client
    C->>API: POST /api/labs/bgp-lab/deploy
    API->>LM: deploy_lab(bgp-lab)
    LM->>GT: execute clab-tools bootstrap
    GT-->>LM: deployment result
    LM-->>API: deployment status
    API-->>C: task_id response
    C-->>CLI: JSON response
    CLI-->>U: formatted output
```

### Web UI Flow

```mermaid
sequenceDiagram
    participant U as User
    participant WEB as Web Browser
    participant API as Flask API
    participant LM as LabManager

    U->>WEB: click deploy button
    WEB->>API: fetch('/api/labs/lab-id/deploy')
    API->>LM: deploy_lab(lab-id)
    LM-->>API: task_id
    API-->>WEB: JSON response
    
    loop Status Polling
        WEB->>API: fetch('/api/tasks/task-id')
        API-->>WEB: task status
    end
    
    WEB-->>U: deployment complete notification
```

### Backend Processing Flow

```mermaid
graph TD
    A[API Request] --> B{Validate Input}
    B -->|Invalid| C[Return 400 Error]
    B -->|Valid| D[LabManager.method()]
    D --> E{Check Prerequisites}
    E -->|Missing| F[Return Error]
    E -->|OK| G[Execute Operation]
    G --> H{Operation Type}
    H -->|Git| I[GitOps.method()]
    H -->|Deploy| J[ClabRunner.run()]
    H -->|NetBox| K[NetBox.allocate()]
    I --> L[Return Result]
    J --> L
    K --> L
    L --> M[Format Response]
    M --> N[Return JSON]
```

## Class Relationships

### Core Module UML

```mermaid
classDiagram
    class LabManager {
        +config: Config
        +git_ops: GitOperations
        +clab_runner: ClabRunner
        +netbox: NetBoxClient
        +state: dict
        +list_repos() dict
        +add_repo(url) dict
        +deploy_lab(lab_id, version) dict
        +destroy_lab(lab_id) dict
        +get_deployments() dict
    }
    
    class GitOperations {
        +git_cmd: str
        +clone(url, path) dict
        +pull(path) dict
        +checkout(path, version) dict
        +get_tags(path) list
    }
    
    class ClabRunner {
        +clab_tools_cmd: str
        +config: Config
        +run_bootstrap(lab_path) dict
        +run_teardown(lab_path) dict
        +stream_output(command) generator
    }
    
    class NetBoxClient {
        +enabled: bool
        +url: str
        +token: str
        +allocate_ips(prefix, count) list
        +register_devices(devices) dict
        +release_ips(ips) dict
    }
    
    LabManager --> GitOperations
    LabManager --> ClabRunner
    LabManager --> NetBoxClient
```

### API Module Structure

```mermaid
classDiagram
    class FlaskApp {
        +lab_manager: LabManager
        +config: Config
        +register_blueprints()
        +serve_static()
    }
    
    class ReposAPI {
        +GET /api/repos
        +POST /api/repos
        +PUT /api/repos/lab_id
        +DELETE /api/repos/lab_id
    }
    
    class LabsAPI {
        +GET /api/labs
        +POST /api/labs/lab_id/deploy
        +POST /api/labs/lab_id/destroy
        +GET /api/labs/lab_id/status
        +GET /api/labs/lab_id/logs
    }
    
    class TasksAPI {
        +GET /api/tasks/task_id
    }
    
    class HealthAPI {
        +GET /api/health
        +GET /api/config
    }
    
    class SettingsAPI {
        +GET /api/config/settings
        +POST /api/config/settings
    }
    
    FlaskApp --> ReposAPI
    FlaskApp --> LabsAPI
    FlaskApp --> TasksAPI
    FlaskApp --> HealthAPI
    FlaskApp --> SettingsAPI
```

## Data Flow Patterns

### Repository Management Flow

```mermaid
graph TD
    A[Add Repository Request] --> B[Validate Git URL]
    B --> C[GitOps.clone()]
    C --> D[Read lab-metadata.yaml]
    D --> E[Parse Lab Information]
    E --> F[Update State File]
    F --> G[Return Lab Info]
    
    H[Update Repository] --> I[GitOps.pull()]
    I --> J[GitOps.get_tags()]
    J --> K[Update Metadata]
    K --> L[Return Changes]
```

### Lab Deployment Flow

```mermaid
graph TD
    A[Deploy Request] --> B[Validate Lab Exists]
    B --> C[Check Version/Tag]
    C --> D[GitOps.checkout()]
    D --> E{NetBox Enabled?}
    E -->|Yes| F[NetBox.allocate_ips()]
    E -->|No| G[Use Static IPs]
    F --> H[Update nodes.csv]
    G --> H
    H --> I[ClabRunner.run_bootstrap()]
    I --> J[Monitor Process]
    J --> K[Update Deployment State]
    K --> L[Return Success]
    
    M[Error] --> N[Cleanup Resources]
    N --> O[Return Error]
```

## Component Interactions

### Frontend-Backend Communication

```mermaid
graph LR
    subgraph Frontend
        CLI[CLI Client]
        WEB[Web UI]
    end
    
    subgraph Backend
        API[Flask API]
        LM[LabManager]
        CORE[Core Modules]
    end
    
    subgraph External
        GIT[Git Repos]
        CLAB[clab-tools]
        NB[NetBox]
    end
    
    CLI -->|HTTP/JSON| API
    WEB -->|HTTP/JSON| API
    API --> LM
    LM --> CORE
    CORE --> GIT
    CORE --> CLAB
    CORE --> NB
```

### State Management

```mermaid
graph TD
    A[Application Start] --> B[Load Config]
    B --> C[Load State File]
    C --> D[Initialize Components]
    
    E[API Request] --> F[LabManager Method]
    F --> G[Update Internal State]
    G --> H[Persist to File]
    H --> I[Return Response]
    
    J[Background Task] --> K[Update State]
    K --> L[Save State]
    L --> M[Notify Completion]
```

## Technology Stack

### Backend Stack
- **Flask**: Web framework and API server
- **Requests**: HTTP client for external APIs
- **GitPython**: Alternative Git operations
- **pynetbox**: NetBox API client
- **subprocess**: External tool execution

### Frontend Stack
- **Click**: CLI framework
- **Rich**: Terminal formatting and UI
- **Vanilla JavaScript**: Web UI (no frameworks)
- **Fetch API**: HTTP client for web UI

### External Integrations
- **Git**: Repository management
- **clab-tools**: Containerlab deployment
- **NetBox**: IP address management
- **SSH**: Remote execution capabilities

## Key Design Patterns

1. **API-First Architecture**: All functionality exposed via REST API
2. **Command Pattern**: CLI commands as discrete operations
3. **Factory Pattern**: LabManager orchestrates all operations
4. **Observer Pattern**: Task status polling for async operations
5. **Strategy Pattern**: Different deployment strategies (local/remote)

This architecture provides a clean separation of concerns, making the system maintainable and extensible for future enhancements.