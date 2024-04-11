---
status: "proposed"
---
# Add an event stream to the TAMS API

## Context and Problem Statement

Many process rely on waiting for something to happen and then taking an action, for example waiting for a Flow to be created or a particular timerange to become available, before reading it in to another process.
As it stands, clients must continually poll the API to wait for an update, which is inefficient.
A push based notification approach would both allow clients to respond to notification events more quickly, and consume fewer resources both on the API server and the clients.

## Considered Options

* Option 1: Specify a/a number of supported notification mechanisms that clients can subscribe to
* Option 2: Specify only the content of notification messages
* Option 2a: Specify the content of notification messages, plus some example implementations
* Option 3: Provide a telemetry output which can also be used to trigger other actions

## Decision Outcome

Chosen option: Option 2a: Specify the content of notification messages, plus some example implementations, because it allows flexibility in the notification mechanism, while providing a framework to document known mechanisms.

### Implementation

Implemented by <https://github.com/bbc/tams/pull/39>

## Pros and Cons of the Options

### Option 1: Specify a/a number of supported notification mechanisms that clients can subscribe to

Document a mechanism that API servers must implement to provide push notifications, such as AWS SNS topics, use of Apache Kafka, MQTT or sending webhooks to specified subscribe URLs.
Also document the messages that should be sent, and a mechanism to allow clients to subscribe to messages of interest.

* Good, because it provides a fully specified method that can be integrated with all clients.
* Good, because it allows the messages to be semantically relevant to the API, rather than the very "noisy" approach proposed in Option 3.
* Neutral, because servers and clients will have to negotiate to choose a method they both support.
* Bad, because the method(s) chosen will inevitably constrain out some options.

### Option 2: Specify only the content of notification messages

Document the messages that will be sent in response to certain events, without stipulating exactly how those messages are sent.

* Good, because it allows implementations considerable flexibility in the approach they adopt.
  For example one implementation could allow clients to provide a webhook URL, and another could use a managed event bus like AWS EventBridge.
* Bad, because additional implementation-specific documentation is required.
* Bad, because a client may not know in advance which mechanisms a server implements.
  However it may be possible to use polling as a fallback, and responding to notifications is likely to be a separate implementation to a regular TAMS client anyway.

### Option 2a: Specify the content of notification messages, plus some example implementations

As with Option 2, but also specify at least one example mechanism.
In addition, add a space to the `service` endpoint that signals which notification mechanisms this implementation supports, with an option to define new mechanisms not originally present.

* Good, because it retains the flexibility of Option 2 if implementations aren't required to use one of the examples.
* Good, because it helps build consensus, especially if other implementations use the example.
* Good, because it provides a way to signal what an API implementation supports.
* Neutral, because further example implementations need to be managed and added to the API documentation in due course.

### Option 3: Provide a telemetry output which can also be used to trigger other actions

Stipulate that implementations supply a telemetry feed of logs, metrics and traces; for example using [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/).
While primarily this is intended to be used for observability of the service, it could also be used to trigger events in other systems using the same data stream.

* Good, because it uses a standard, well-defined format.
* Bad, because the resulting data stream will be very noisy (containing traces of activity throughout the entire API server).
* Bad, because the output logs and traces may leak detail intended to be internal to the API.
