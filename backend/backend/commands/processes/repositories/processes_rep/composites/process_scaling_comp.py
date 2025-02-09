from dataclasses import dataclass
from typing import Optional, Tuple

from backend.commands.processes.models.process_mod.process_ai_val import ProcessAIVal
from backend.commands.processes.models.process_mod.process_bicubic_val import (
    ProcessBicubicVal,
)
from backend.commands.processes.models.process_mod.process_resolution_val import (
    ProcessResolutionVal,
)
from backend.helpers.exception_utils import ServerInternalErrorException


@dataclass
class ProcessScalingComp:
    value: ProcessBicubicVal | ProcessAIVal

    @classmethod
    def _generate(
        cls,
        scaling_bicubic_target_width: Optional[int],
        scaling_bicubic_target_height: Optional[int],
        scaling_ai_scale: Optional[int],
    ) -> "ProcessScalingComp":
        if scaling_bicubic_target_width and scaling_bicubic_target_height:
            return ProcessScalingComp(
                ProcessBicubicVal(
                    ProcessResolutionVal(
                        scaling_bicubic_target_width, scaling_bicubic_target_height
                    )
                )
            )
        elif scaling_ai_scale and (
            scaling_ai_scale == 2 or scaling_ai_scale == 3 or scaling_ai_scale == 4
        ):
            return ProcessScalingComp(ProcessAIVal(scaling_ai_scale))
        else:
            raise ServerInternalErrorException(
                f"Composite generation error: '{cls.__name__}'."
            )

    def __composite_values__(
        self,
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        match self.value:
            case ProcessBicubicVal(target=target):
                return target.width, target.height, None
            case ProcessAIVal(scale=scale):
                return None, None, scale
