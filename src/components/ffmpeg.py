import concurrent
import subprocess
from typing import IO, Optional, Union, override

from ffmpeg import FFmpeg as BaseFFmpeg
from ffmpeg.errors import FFmpegAlreadyExecuted, FFmpegError
from ffmpeg.utils import create_subprocess, ensure_io  # type: ignore


class FFmpeg(BaseFFmpeg):
    @override
    def execute(self, stream: Optional[Union[bytes, IO[bytes]]] = None, timeout: Optional[float] = None) -> bytes:
        """Overridden version of Ffmpeg.execute() to fix keyboard interruptions not working correctly in some cases."""
        if self._executed:
            raise FFmpegAlreadyExecuted("FFmpeg is already executed", arguments=self.arguments)

        self._executed = False
        self._terminated = False

        if stream is not None:
            stream = ensure_io(stream)

        self.emit("start", self.arguments)

        self._process = create_subprocess(  # type: ignore
            self.arguments,
            bufsize=0,
            stdin=subprocess.PIPE if stream is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:  # type: ignore
            self._executed = True
            futures = [  # type: ignore
                executor.submit(self._write_stdin, stream),  # type: ignore
                executor.submit(self._read_stdout),  # type: ignore
                executor.submit(self._handle_stderr),  # type: ignore
                executor.submit(self._process.wait, timeout),  # type: ignore
            ]
            pending = futures  # type: ignore
            try:
                while pending:
                    done, pending = concurrent.futures.wait(  # type: ignore
                        futures,
                        timeout=1,
                        return_when=concurrent.futures.FIRST_EXCEPTION,  # type: ignore
                    )
            except KeyboardInterrupt as e:
                self.terminate()
                executor.shutdown(wait=True, cancel_futures=True)  # type: ignore
                raise e
            self._executed = False

            for future in done:  # type: ignore
                exception = future.exception()  # type: ignore
                if exception is not None:
                    self._process.terminate()  # type: ignore
                    concurrent.futures.wait(pending)  # type: ignore

                    raise exception

        if self._process.returncode == 0:  # type: ignore
            self.emit("completed")
        elif self._terminated:
            self.emit("terminated")
        else:
            raise FFmpegError.create(message=futures[2].result(), arguments=self.arguments)  # type: ignore

        return futures[1].result()  # type: ignore
