from abc import ABC, abstractmethod


class Driver(ABC):

    @abstractmethod
    def start(self) -> None:
        """
        Starts the driver
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the driver
        """

    @abstractmethod
    def generate(self) -> str:
        """
        Generates a value if the driver is running
        """
