from typing import Coroutine, TypeAlias, Any, Literal
from enum import IntEnum
from collections.abc import Sequence, Iterator, Callable
from math import inf
from typing import Protocol, Self, TypeVar, Never, Concatenate
from contextlib import AbstractContextManager
from .core import *

SenderT = TypeVar('SenderT', bound='baseItem')
TargetT = TypeVar('TargetT', bound='baseItem')

class DCGCallable0(Protocol):
    def __call__(self, /) -> Any:
        ...

class DCGCallable1(Protocol[SenderT]):
    def __call__(self,
                 sender : SenderT,
                 /) -> Any:
        ...

class DCGCallable2(Protocol[SenderT, TargetT]):
    def __call__(self,
                 sender : SenderT,
                 target : TargetT,
                 /) -> Any:
        ...

class DCGCallable3(Protocol[SenderT, TargetT]):
    def __call__(self,
                 sender : SenderT,
                 target : TargetT,
                 value : Any,
                 /) -> Any:
        ...

class DCGCallable0Kw(Protocol):    
    def __call__(self, /, **kwargs) -> Any:
        ...

class DCGCallable1Kw(Protocol[SenderT]):
    def __call__(self,
                 sender : SenderT,
                 /,
                 **kwargs : Any) -> Any:
        ...

class DCGCallable2Kw(Protocol[SenderT, TargetT]):
    def __call__(self,
                 sender : SenderT,
                 target : TargetT,
                 /,
                 **kwargs : Any) -> Any:
        ...

class DCGCallable3Kw(Protocol[SenderT, TargetT]):
    def __call__(self,
                 sender : SenderT,
                 target : TargetT,
                 value : Any,
                 /,  
                 **kwargs : Any) -> Any:
        ...


DCGCallable = DCGCallable0 | DCGCallable1 | DCGCallable2 | DCGCallable3 | DCGCallable0Kw | DCGCallable1Kw | DCGCallable2Kw | DCGCallable3Kw


class Callback(DCGCallable3[SenderT, TargetT]):
    """
    Wrapper class that automatically encapsulates callbacks.

    Callbacks in DCG mode can take up to 3 arguments:
        - source_item: the item to which the callback was attached
        - target_item: the item for which the callback was raised.
            Is only different to source_item for handlers' callback.
        - call_info: If applicable information about the call (key button, etc)

    This class adapts callbacks with fewer parameters to the full 3-parameter form.
    """
    def __init__(self, callback: DCGCallable) -> None:
        ...
    
    def __call__(self, sender: SenderT, target: TargetT, value: Any) -> Any:
        """
        Call the wrapped callback with appropriate number of arguments.
        
        Automatically adapts between callbacks that accept 0, 1, 2, or 3 arguments.
        """
        ...

    @property
    def callback(self) -> DCGCallable:
        """(Read-only) The original wrapped callback
        """
        ...


class TaskSubmitter(Protocol):
    def submit(self, fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
        ...

class AnyTaskSubmitter(Protocol):
    def submit(self, fn: Callable[..., Any] | Coroutine, /, *args: Any, **kwargs: Any) -> Any:
        ...


Color = int | tuple[int, int, int] | tuple[int, int, int, int] | tuple[float, float, float] | tuple[float, float, float, float] | Sequence[int] | Sequence[float]


class wrap_mutex:
    def __init__(self, target) -> None:
        ...
    
    def __enter__(self): # -> None:
        ...
    
    def __exit__(self, exc_type, exc_value, traceback): # -> Literal[False]:
        ...
    


class wrap_this_and_parents_mutex:
    def __init__(self, target) -> None:
        ...
    
    def __enter__(self): # -> None:
        ...
    
    def __exit__(self, exc_type, exc_value, traceback): # -> Literal[False]:
        ...


class Gamepad:
    """
    Represents a single gamepad/controller slot (0-7).

    Use ``viewport.gamepads[i]`` to get the Gamepad for slot *i*.
    Query button and axis state each frame via polling methods.
    """
    @property
    def slot(self) -> int:
        """Slot index (0-7) for this controller."""
        ...

    @property
    def connected(self) -> bool:
        """True if a physical controller is plugged into this slot."""
        ...

    @property
    def name(self) -> str:
        """Hardware controller name reported by SDL3, or '' if empty.

        This is the device name SDL3 obtains from the underlying
        driver / HID descriptor (e.g. ``'Xbox Wireless Controller'``,
        ``'PS5 Controller'``, ``'Nintendo Switch Pro Controller'``).
        It is read-only and identifies the *hardware*, not the player
        using it. To associate a player label with a slot, keep a
        separate mapping such as ``player_names[gamepad.slot] = 'P1'``.
        """
        ...

    def is_button_down(self, button: 'GamepadButton') -> bool:
        """Return True while *button* is held down."""
        ...

    def is_button_pressed(self, button: 'GamepadButton') -> bool:
        """Return True only on the frame *button* transitioned from up to down.

        Edge-detection state is cleared at the start of each ``render_frame()``
        call, so this returns True for exactly one frame per press.
        """
        ...

    def is_button_released(self, button: 'GamepadButton') -> bool:
        """Return True only on the frame *button* transitioned from down to up.

        Edge-detection state is cleared at the start of each ``render_frame()``
        call, so this returns True for exactly one frame per release.
        """
        ...

    def get_axis(self, axis: 'GamepadAxis') -> float:
        """Return the current axis value (-1.0 to 1.0 for sticks, 0.0 to 1.0 for triggers)."""
        ...

try:
    from collections.abc import Buffer
    Array: TypeAlias = memoryview | bytearray | bytes | Sequence[Any] | Buffer
except ImportError:
    Array: TypeAlias = memoryview | bytearray | bytes | Sequence[Any] | "np.ndarray[Any, Any]"

