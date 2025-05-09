# MeritPath

## System Architecture
![System Architecture Diagram](docs/static/img/architecture.png)

Our system uses a containerized architecture built on AWS ECS for scalable processing of both synchronous requests and asynchronous tasks.

### Components

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