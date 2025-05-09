# MeritPath

## 1. System Architecture
![System Architecture Diagram](docs/static/img/architecture.png)

Our system uses a containerized architecture built on AWS ECS for scalable processing of both synchronous requests and asynchronous tasks.

### 1.1 Components

- **ECS Cluster**: Contains our containerized services
 - **Backend Service**: Handles API requests, data validation, and business logic. Auto-scales based on CPU/memory usage to maintain responsiveness during traffic spikes.
 - **Worker Service**: Processes background jobs that require intensive computation. Auto-scales based on SQS queue depth to efficiently handle varying workloads.

- **Application Load Balancer**: Routes incoming client requests to the Backend Service, provides SSL termination, and ensures high availability.

- **SQS Queue**: Facilitates asynchronous communication between services. The Backend Service sends jobs to the queue, which the Worker Service retrieves and processes independently.

- **Client Applications**: External applications that interact with our system through the API endpoints exposed by the Backend Service.

This architecture provides several advantages:
- Separation of concerns between immediate request handling and background processing
- Independent scaling for different workload types
- High availability through AWS managed services
- Fault isolation between components


### 1.2 Supabase Integration

For real-time updates and job tracking, we implemented Supabase subscriptions that:

1. **Track Job Status**: We created tables in Supabase to store job information and results, allowing us to track the status of jobs as they move through the system.

2. **Real-time Updates**: On the detail page for each job, we set up a Supabase subscription that listens for changes to job records, enabling the UI to update in real-time as job status changes.

3. **Simplified Architecture**: By using Supabase subscriptions, we eliminated the need for webhook callbacks or continuous polling, reducing complexity and improving the user experience.


This architecture provides several advantages:
- Separation of concerns between immediate request handling and background processing
- Independent scaling for different workload types
- High availability through AWS managed services
- Fault isolation between components
- Real-time updates through Supabase subscriptions


## 2. Database Design
Our database is structured to efficiently store and query citation data while supporting asynchronous processing:

### Core Tables
- **users**: Stores registered users with their Semantic Scholar IDs and basic metrics
- **papers**: Contains academic paper metadata with unique Semantic Scholar identifiers
- **citers**: Tracks researchers who have cited our users' papers
- **citations**: Represents direct paper-to-paper citation relationships

### Relationship Tables
- **user_papers**: Links users to the papers they've authored
- **user_citers**: Associates users with researchers who cite their work
- **citer_citations**: Connects citers with the specific citations they've made

### Processing Tables
- **jobs**: Tracks background processing tasks with their current status
- **job_results**: Stores the outcome of completed jobs for retrieval

This normalized design provides several advantages:
- **Efficient Querying**: Direct relationships between entities allow for precise data retrieval
- **Memory Optimization**: Information is stored in the database as it's processed rather than kept in memory
- **Incremental Processing**: Paper-by-paper processing enables controlled memory usage for large datasets
- **Real-time Updates**: Through Supabase subscriptions, the frontend receives immediate notifications when job statuses change

The database schema supports both the immediate needs of the application and future expansion as we add more complex citation analysis features.