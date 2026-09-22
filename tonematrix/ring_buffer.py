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

        if capacity < 1:
            raise ValueError(f"Capacity cannot be less than 1. Received {capacity}")

        self._data = array("d", [0] * capacity)
        self._front = 0
        self._rear = 0
        self._size = 0
        self._capacity = capacity

        """Create an empty buffer that can hold `capacity` items.

        Set up four things:
          * self._data  - array("d") of `capacity` zeros
          * self._front - index of the least recently enqueued item
          * self._rear  - index one past the most recently enqueued item
          * self._size  - how many items are in the buffer right now

        Raise ValueError if capacity is less than 1.
        """

    def capacity(self):
        """The most items this buffer can hold."""

        return self._capacity

    def size(self):
        """How many items are in the buffer right now."""

        return self._size

    def is_empty(self):

        if self._size == 0:
            return True

    def is_full(self):

        if self._size == self._capacity:
            return True

    def enqueue(self, x):
        """Add x at the rear. 
        
        Raise IndexError if the buffer is already full.
        """

        if self.is_full():
            raise IndexError("Buffer is already full.")

        self._data[self._rear] = x

        if self._rear == self._capacity - 1:
            self._rear = 0
        else:
            self._rear += 1
        self._size += 1

    def dequeue(self):
        """Remove and return the item at the front. 

        Raise IndexError if the buffer is empty.
        """
    
        if self.is_empty():
            raise IndexError("Buffer is empty.")

        front_item = self._data[self._front]

        if self._front == self._capacity - 1:
            self._front = 0
        else:
            self._front += 1
        self._size -= 1

        return front_item

    def peek(self):
        """Return the item at the front without removing it.

        Raise IndexError if the buffer is empty.
        """

        if self.is_empty():
            raise IndexError("Buffer is empty.")

        return self._data[self._front]

    def __len__(self):
        """So that len(buffer) works. Provided, once size() works."""
        return self.size()
