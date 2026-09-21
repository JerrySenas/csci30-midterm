"""Part 1: a fixed-capacity ring buffer.

A queue that never grows. It holds at most `capacity` floats; enqueueing into
a full buffer or dequeueing from an empty one is an error, not a resize.

Rules for this file:
  * The storage is `array("d", ...)` of exactly `capacity` elements,
    allocated once in __init__ and never replaced. Keep it in `self._data`.
  * No list, no dict, no collections.deque, no NumPy. This is checked.
  * Every operation must run in constant time. In particular, dequeue() must
    not shuffle the remaining items down by one.
"""

from array import array


class RingBuffer:
    """A circular queue of floats with a fixed capacity."""

    def __init__(self, capacity):
        """Create an empty buffer that can hold `capacity` items.

        Set up four things:
          * self._data  - array("d") of `capacity` zeros
          * self._front - index of the least recently enqueued item
          * self._rear  - index one past the most recently enqueued item
          * self._size  - how many items are in the buffer right now

        Raise ValueError if capacity is less than 1.
        """
        # TODO (Milestone 2)
        raise NotImplementedError("RingBuffer.__init__")

    def capacity(self):
        """The most items this buffer can hold."""
        # TODO (Milestone 2)
        raise NotImplementedError("RingBuffer.capacity")

    def size(self):
        """How many items are in the buffer right now."""
        # TODO (Milestone 2)
        raise NotImplementedError("RingBuffer.size")

    def is_empty(self):
        # TODO (Milestone 2)
        raise NotImplementedError("RingBuffer.is_empty")

    def is_full(self):
        # TODO (Milestone 2)
        raise NotImplementedError("RingBuffer.is_full")

    def enqueue(self, x):
        """Add x at the rear. 
        
        Raise IndexError if the buffer is already full.
        """
        # TODO (Milestone 3)
        raise NotImplementedError("RingBuffer.enqueue")

    def dequeue(self):
        """Remove and return the item at the front. 

        Raise IndexError if the buffer is empty.
        """
        # TODO (Milestone 3)
        raise NotImplementedError("RingBuffer.dequeue")

    def peek(self):
        """Return the item at the front without removing it.

        Raise IndexError if the buffer is empty.
        """
        # TODO (Milestone 3)
        raise NotImplementedError("RingBuffer.peek")

    def __len__(self):
        """So that len(buffer) works. Provided, once size() works."""
        return self.size()
