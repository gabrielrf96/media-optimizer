from __future__ import annotations

from typing import Any, Optional

class Stream(object):
    def filter(  # pylint: disable=redefined-builtin
        self,
        stream_spec: str,
        filter_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Stream: ...
    def output(self, *streams_and_filename: Any, **kwargs: Any) -> Stream: ...
    def overwrite_output(self, stream: Optional[Any] = None) -> Stream: ...
