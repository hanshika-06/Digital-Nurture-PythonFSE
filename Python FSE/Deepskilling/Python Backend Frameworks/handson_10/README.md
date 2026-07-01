# Hands-On 10: Microservices Architecture - Concepts & Decomposition

This directory contains the decomposed Course Management API built with Flask. The application is divided into two backend services and a Gateway proxy.

## Decomposed Monolith: Bounded Contexts

Below is the architectural breakdown of the services:

| Service Name | Responsibility | Endpoints It Owns | Database It Owns |
| :--- | :--- | :--- | :--- |
| **Course Service** | Manages departments and course listings, including credits and structural associations. | `GET /api/departments/`<br>`POST /api/departments/`<br>`GET /api/departments/{id}/`<br>`GET /api/courses/`<br>`POST /api/courses/`<br>`GET/PUT/DELETE /api/courses/{id}/` | `courses.db` (SQLite) |
| **Student Service** | Manages student profiles and handles course enrollments. Calls Course Service to validate course availability. | `GET /api/students/`<br>`POST /api/students/`<br>`GET/PUT/DELETE /api/students/{id}/`<br>`POST /api/students/{id}/enroll` | `students.db` (SQLite) |
| **API Gateway** | Acts as a single entry point proxy. Routes client traffic to appropriate downstream microservice. | `/api/courses/*` -> Course Service (Port 5001)<br>`/api/students/*` -> Student Service (Port 5002) | None |

---

## Inter-Service Communication: Synchronous (HTTP) vs Asynchronous (Message Queue)

In a microservice architecture, services must communicate with each other. Here is an analysis of the two core patterns:

### 1. Synchronous Communication (HTTP / REST / gRPC)
* **Description**: The calling service sends a request and blocks/waits until it receives a response from the target service (e.g. Student Service waiting on Course Service via `requests.get()`).
* **Trade-offs**:
  * **Pros**: 
    * Easy to implement, understand, and debug.
    * Immediate feedback (e.g. you know instantly if the course exists and can return a validation error or 201 Created directly to the user).
  * **Cons**:
    * **Temporal Coupling**: Both services must be online and active at the same time. If Course Service is down, Student Service's enrollment endpoint fails (returns 503).
    * **Cascading Failures**: A delay in Course Service causes Student Service threads to block, potentially exhausting resources.

### 2. Asynchronous Communication (Message Queues: RabbitMQ, Apache Kafka)
* **Description**: The calling service publishes an event (e.g. "enrollment requested") to a broker. The recipient service consumes this message whenever it is available. The caller does not block.
* **Trade-offs**:
  * **Pros**:
    * **Decoupled Availability**: Even if the Course/Notification service is offline, the enrollment request is stored safely in the queue and processed later.
    * **Scalability & Load Smoothing**: Handles traffic spikes cleanly by queueing tasks rather than crashing servers.
  * **Cons**:
    * **Eventual Consistency**: Data is not updated instantly. The client gets an "accepted" response and must poll or use websockets to find out if it succeeded.
    * **Complexity**: High setup and operational overhead (managing message brokers, retry policies, dead-letter queues, idempotent consumers).

### When to use a Message Queue (e.g., RabbitMQ or Kafka)
Use a message queue like RabbitMQ or Kafka in the following scenarios:
1. **Non-Blocking Processes**: E.g., sending email/SMS confirmations, generating invoices, processing video uploads. The client doesn't need the result immediately.
2. **High throughput/Data Pipelines**: E.g., Kafka is preferred for streaming analytics, logging, tracking user clickstreams, or syncing search index databases.
3. **Cross-Service Events**: When multiple departments or services need to know about an action (e.g., when a user purchases an item, inventory, shipping, and notification services all consume the same message to initiate their tasks).
