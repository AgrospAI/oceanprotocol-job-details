from typing import Callable, Generic, TypeVar, get_origin

T = TypeVar("T")


class PluginRegistry(Generic[T]):
    _registry: dict[type[T], dict[str, list[type[T]]]] = {}

    @classmethod
    def register(
        cls,
        plugin: type[T],
        interface: type[T],
        supported: list[str] | str,
    ) -> type[T]:
        if not issubclass(plugin, interface):
            raise TypeError(
                f"{plugin.__name__} does not implement {interface.__name__}"
            )

        if isinstance(supported, str):
            supported = [supported]

        iface_registry = cls._registry.setdefault(interface, {})
        for sup in supported:
            iface_registry.setdefault(sup, []).append(plugin)

        return plugin

    @classmethod
    def get(cls, interface: type[T], sup: str = "") -> type[T]:
        plugins = cls._registry.get(interface, {}).get(sup, [])
        assert plugins, f"Class {interface} has no plugin supporting {sup}"
        return plugins[-1]

    @classmethod
    def get_instance(cls, interface: type[T], sup: str = "", *args, **kwargs) -> T:
        instance_class = cls.get(interface, sup)
        return instance_class(*args, **kwargs)

    @classmethod
    def representation(cls) -> dict:
        return {
            k: {kk: [vvv.__name__ for vvv in vv] for kk, vv in v.items()}
            for k, v in cls._registry.items()
        }


def register(supported: str | list[str] = "") -> Callable[[type[T]], type[T]]:
    """Register the decorated class to its implementing interfaces.

    Args:
        supported (str | list[str], optional): Data to decide which implementation use. Defaults to "".
    """

    def decorator(plugin_cls: type[T]) -> type[T]:
        bases = [b for b in plugin_cls.__bases__ if b is not object]
        if not bases:
            raise TypeError(
                f"Plugin {plugin_cls.__name__} has no base class to infer interface"
            )

        for base in bases:
            PluginRegistry.register(plugin_cls, base, supported)
        return plugin_cls

    return decorator


def inject(interface: type[T], supported: str, *args, **kwargs) -> T:
    """Inject the adient implementation of the needed interface that supports the needed type.

    Args:
        interface (type[T]): interface that the instance has to implement.
        supported (str): supported data type.

    Returns:
        T: instance implementing interface of the supported type.
    """

    base_interface = get_origin(interface) or interface

    return PluginRegistry.get_instance(base_interface, supported, *args, **kwargs)
