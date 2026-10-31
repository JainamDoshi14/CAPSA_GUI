"""Application entry point for Transmission Line Studio."""

from app import TransmissionLineStudio


def main() -> None:
    app = TransmissionLineStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
