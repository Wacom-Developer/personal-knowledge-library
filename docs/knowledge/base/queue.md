Module knowledge.base.queue
===========================

Classes
-------

`MessageRate(rate: float)`
:   Represents the rate at which messages are sent or processed.
    
    This class models a single attribute that tracks the speed or frequency
    of messaging events, typically measured as a float. It can be used in
    applications or systems where monitoring, regulating, or analyzing
    message throughput is required.
    
    Attributes
    ----------
    rate : float
        The rate at which messages are sent or processed.

    ### Static methods

    `parse_json(json_str: str) ‑> knowledge.base.queue.MessageRate`
    :   Parse a JSON string and return a MessageRate instance.

    ### Instance variables

    `rate: float`
    :   The rate at which messages are sent or processed.

`MessageStats(publish: int | None = None, publish_details: knowledge.base.queue.MessageRate | None = None, deliver: int | None = None, deliver_details: knowledge.base.queue.MessageRate | None = None, ack: int | None = None, ack_details: knowledge.base.queue.MessageRate | None = None)`
:   Represents statistics related to message publishing, delivery, and acknowledgments.
    
    This class is used to store statistics about messages such as their publication count,
    delivery count, acknowledgment count, and the corresponding details about rates.
    It serves as a structured model for handling message statistics data.
    
    Attributes
    ----------
    publish : Optional[int]
        The count of published messages.
    publish_details : Optional[MessageRate]
        Detailed rate information related to message publishing.
    deliver : Optional[int]
        The count of delivered messages.
    deliver_details : Optional[MessageRate]
        Detailed rate information related to message delivery.
    ack : Optional[int]
        The count of acknowledged messages.
    ack_details : Optional[MessageRate]
        Detailed rate information related to message acknowledgments.

    ### Static methods

    `parse_json(json_str: str) ‑> knowledge.base.queue.MessageStats`
    :   Parse a JSON string and return a MessageStats instance.

    ### Instance variables

    `ack: int | None`
    :   The count of acknowledged messages.

    `ack_details: knowledge.base.queue.MessageRate | None`
    :   Detailed rate information related to message acknowledgments.

    `deliver: int | None`
    :   The count of delivered messages.

    `deliver_details: knowledge.base.queue.MessageRate | None`
    :   Detailed rate information related to message delivery.

    `publish: int | None`
    :   The count of published messages.

    `publish_details: knowledge.base.queue.MessageRate | None`
    :   Detailed rate information related to message publishing.

`QueueCount(queue_name: str, count: int)`
:   Represents a model for maintaining a queue's name and its count.
    
    This class is primarily designed to encapsulate the queue name and the
    count of items or occurrences associated with it. It can be used
    in various queue-related workflows or systems where such data is required.
    
    Attributes
    ----------
    queue_name : str
        The name of the queue being represented.
    count : int
        The count of items or occurrences associated with the queue.

    ### Static methods

    `parse_json(data: Dict[str, Any]) ‑> knowledge.base.queue.QueueCount`
    :   Parse a JSON string and return a QueueCount instance.
        
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary containing the queue name and count.
        
        Returns
        -------
        result: QueueCount
            An instance of QueueCount.

    ### Instance variables

    `count: int`
    :   The count of items or occurrences associated with the queue.

    `queue_name: str`
    :   The name of the queue.

`QueueMonitor(name: str, vhost: str, state: str, messages: int, messages_ready: int, messages_unacknowledged: int, consumers: int, memory: int, message_stats: knowledge.base.queue.MessageStats | None = None)`
:   Represents a monitor for a queue in a message broker.
    
    This class is used to monitor and manage the state and statistics of a
    message queue. It provides details such as the name of the queue,
    virtual host, current state, message-related statistics, and resource
    usage. It can be integrated into monitoring or operational tools to
    track queue performance and behavior.
    
    Attributes
    ----------
    name : str
        Name of the queue being monitored.
    vhost : str
        Name of the virtual host to which the queue belongs.
    state : str
        Current state of the queue (e.g., running, idle).
    messages : int
        Total number of messages in the queue.
    messages_ready : int
        Number of messages ready to be delivered to consumers.
    messages_unacknowledged : int
        Number of messages delivered to consumers but not yet acknowledged.
    consumers : int
        Number of consumers currently subscribed to the queue.
    memory : int
        Amount of memory used by the queue (in bytes).
    message_stats : Optional[MessageStats]
        Detailed statistics about messages in the queue, if available.

    ### Static methods

    `parse_json(data: Dict[str, Any]) ‑> knowledge.base.queue.QueueMonitor`
    :   Parse a JSON string and return a QueueMonitor instance.
        
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary containing queue monitor data.
        
        Returns
        -------
        Instance of QueueMonitor.

    ### Instance variables

    `consumers: int`
    :   Number of consumers currently subscribed to the queue.

    `memory: int`
    :   Amount of memory used by the queue (in bytes).

    `message_stats: knowledge.base.queue.MessageStats | None`
    :   Detailed statistics about messages in the queue, if available.

    `messages: int`
    :   Total number of messages in the queue.

    `messages_ready: int`
    :   Number of messages ready to be delivered to consumers.

    `messages_unacknowledged: int`
    :   Number of messages delivered to consumers but not yet acknowledged.

    `name: str`
    :   The name of the queue being monitored.

    `state: str`
    :   Current state of the queue (e.g., running, idle).

    `vhost: str`
    :   Name of the virtual host to which the queue belongs.

`QueueNames(names: List[str])`
:   Represents a model for handling queue names.
    
    This class provides a structure to store and manage names associated with
    queues. It can be useful in systems requiring organization or representation
    of multiple queues. This model ensures type safety and consistency.
    
    Attributes
    ----------
    names : List[str]
        List of names representing different queues.

    ### Static methods

    `parse_json(data: Dict[str, Any]) ‑> knowledge.base.queue.QueueNames`
    :   Parse a JSON string and return a QueueNames instance.
        
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary containing the queue names.

    ### Instance variables

    `names: List[str]`
    :   List of names representing different queues.