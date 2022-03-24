from abc import ABC, abstractmethod


class Driver(ABC):

    @abstractmethod
    def start(self):
        """
        Starts the driver
        """

    @abstractmethod
    def stop(self):
        """
        Stops the driver
        """

    @abstractmethod
    def generate(self):
        """
        Generates a value if the driver is running
        """
