import asyncio
import os
import logging
import subprocess
from pyrtmp import StreamClosedException
from pyrtmp.flv import FLVFileWriter, FLVMediaType
from pyrtmp.session_manager import SessionManager
from pyrtmp.rtmp import SimpleRTMPController, RTMPProtocol, SimpleRTMPServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class RealTimeVideoProcessor(SimpleRTMPController):
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.active_stream = None  # Flag to indicate active stream
        self.flv_writer = None     # Reference to the FLV writer object

    async def on_ns_publish(self, session, message) -> None:
        publishing_name = message.publishing_name
        file_path = os.path.join(self.output_directory, f"{publishing_name}.flv")

        # Create a new FLV writer only when stream starts
        if not self.active_stream:
            self.flv_writer = FLVFileWriter(output=file_path)
            self.active_stream = True
            command = [
                "C:/Users/HP/anaconda3/envs/cvapp/python.exe",
                "c:/Users/HP/Desktop/Code/python/rtmp_receiver/cv_flv_view.py",
                file_path
            ]
            # Start the OpenCV process in a separate process
            #await asyncio.sleep(5)
            self.opencv_process = subprocess.Popen(command)

        

        session.state = self.flv_writer
        await super().on_ns_publish(session, message)

    async def on_metadata(self, session, message) -> None:
        if self.active_stream:
            session.state.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
        await super().on_metadata(session, message)

    async def on_video_message(self, session, message) -> None:
        if self.active_stream:
            session.state.write(message.timestamp, message.payload, FLVMediaType.VIDEO)
        await super().on_video_message(session, message)

    async def on_audio_message(self, session, message) -> None:
        # Handle audio if needed (not used for video streaming)
        pass  # You can implement audio handling here

    async def on_stream_closed(self, session: SessionManager, exception: StreamClosedException) -> None:
        if self.active_stream:
            session.state.close()
            self.flv_writer.close()  # Explicitly close the FLV writer
            self.active_stream = False
            self.flv_writer = None     # Reset FLV writer reference
            self.opencv_process.terminate()
            self.opencv_process = None
            await asyncio.sleep(2)
            os.remove('.flv')  # Delete the FLV file
        self.active_stream = False
        await super().on_stream_closed(session, exception)

class SimpleServer(SimpleRTMPServer):
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        super().__init__()
    
    async def create(self, host: str, port: int):
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: RTMPProtocol(controller=RealTimeVideoProcessor(self.output_directory)),
            host=host,
            port=port,
        )

async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server = SimpleServer(output_directory=current_dir)
    await server.create(host='0.0.0.0', port=1935)
    await server.start()
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
