# ui/base_section.py
class SectionRegistry:
    _frames: dict[str, type] = {}

    @classmethod
    def register(cls, section_type: str):
        def decorator(frame_cls: type):
            cls._frames[section_type] = frame_cls
            return frame_cls
        return decorator

    @classmethod
    def get_frame(cls, section_type: str) -> type:
        return cls._frames[section_type]

    @classmethod
    def available_types(cls) -> list[str]:
        # This will now always reflect whatever's been registered
        return list(cls._frames.keys())
