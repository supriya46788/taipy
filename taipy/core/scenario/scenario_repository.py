import pathlib
from datetime import datetime
from typing import List, Optional

from taipy.core.common import utils
from taipy.core.common.alias import CycleId, PipelineId
from taipy.core.config.config import Config
from taipy.core.cycle.cycle import Cycle
from taipy.core.cycle.cycle_manager import CycleManager
from taipy.core.exceptions.pipeline import NonExistingPipeline
from taipy.core.pipeline.pipeline import Pipeline
from taipy.core.pipeline.pipeline_manager import PipelineManager
from taipy.core.repository import FileSystemRepository
from taipy.core.scenario.scenario import Scenario
from taipy.core.scenario.scenario_model import ScenarioModel


class ScenarioRepository(FileSystemRepository[ScenarioModel, Scenario]):
    def __init__(self):
        super().__init__(model=ScenarioModel, dir_name="scenarios")

    def to_model(self, scenario: Scenario):
        return ScenarioModel(
            id=scenario.id,
            name=scenario._config_id,
            pipelines=self.__to_pipeline_ids(scenario._pipelines.values()),
            properties=scenario._properties.data,
            creation_date=scenario._creation_date.isoformat(),
            master_scenario=scenario._master_scenario,
            subscribers=utils.fcts_to_dict(scenario._subscribers),
            tags=list(scenario._tags),
            cycle=self.__to_cycle_id(scenario._cycle),
        )

    def from_model(self, model: ScenarioModel) -> Scenario:
        scenario = Scenario(
            scenario_id=model.id,
            config_id=model.name,
            pipelines=self.__to_pipelines(model.pipelines),
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            is_master=model.master_scenario,
            tags=set(model.tags),
            cycle=self.__to_cycle(model.cycle),
            subscribers={utils.load_fct(it["fct_module"], it["fct_name"]) for it in model.subscribers},
        )
        return scenario

    @property
    def storage_folder(self) -> pathlib.Path:
        return pathlib.Path(Config.global_config.storage_folder)  # type: ignore

    @staticmethod
    def __to_pipeline_ids(pipelines) -> List[PipelineId]:
        return [pipeline.id for pipeline in pipelines]

    @staticmethod
    def __to_pipelines(pipeline_ids) -> List[Pipeline]:
        pipelines = []
        for _id in pipeline_ids:
            if pipeline := PipelineManager.get(_id):
                pipelines.append(pipeline)
            else:
                raise NonExistingPipeline(_id)
        return pipelines

    @staticmethod
    def __to_cycle(cycle_id: CycleId = None) -> Optional[Cycle]:
        return CycleManager.get(cycle_id) if cycle_id else None

    @staticmethod
    def __to_cycle_id(cycle: Cycle = None) -> Optional[CycleId]:
        return cycle.id if cycle else None
