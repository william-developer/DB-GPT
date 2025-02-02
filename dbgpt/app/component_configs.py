from __future__ import annotations

import logging

from dbgpt.component import SystemApp
from dbgpt._private.config import Config
from dbgpt.configs.model_config import MODEL_DISK_CACHE_DIR
from dbgpt.util.executor_utils import DefaultExecutorFactory
from dbgpt.app.base import WebServerParameters


logger = logging.getLogger(__name__)

CFG = Config()


def initialize_components(
    param: WebServerParameters,
    system_app: SystemApp,
    embedding_model_name: str,
    embedding_model_path: str,
):
    # Lazy import to avoid high time cost
    from dbgpt.model.cluster.controller.controller import controller
    from dbgpt.app.initialization.embedding_component import _initialize_embedding_model
    from dbgpt.app.initialization.serve_initialization import register_serve_apps

    # Register global default executor factory first
    system_app.register(DefaultExecutorFactory)
    system_app.register_instance(controller)

    # Register global default RAGGraphFactory
    # from dbgpt.graph.graph_factory import DefaultRAGGraphFactory

    # system_app.register(DefaultRAGGraphFactory)

    from dbgpt.serve.agent.hub.controller import module_agent

    system_app.register_instance(module_agent)

    from dbgpt.serve.agent.agents.controller import multi_agents

    system_app.register_instance(multi_agents)

    _initialize_embedding_model(
        param, system_app, embedding_model_name, embedding_model_path
    )
    _initialize_model_cache(system_app)
    _initialize_awel(system_app, param)
    # Register serve apps
    register_serve_apps(system_app, CFG)


def _initialize_model_cache(system_app: SystemApp):
    from dbgpt.storage.cache import initialize_cache

    if not CFG.MODEL_CACHE_ENABLE:
        logger.info("Model cache is not enable")
        return

    storage_type = CFG.MODEL_CACHE_STORAGE_TYPE or "disk"
    max_memory_mb = CFG.MODEL_CACHE_MAX_MEMORY_MB or 256
    persist_dir = CFG.MODEL_CACHE_STORAGE_DISK_DIR or MODEL_DISK_CACHE_DIR
    initialize_cache(system_app, storage_type, max_memory_mb, persist_dir)


def _initialize_awel(system_app: SystemApp, param: WebServerParameters):
    from dbgpt.core.awel import initialize_awel
    from dbgpt.configs.model_config import _DAG_DEFINITION_DIR

    # Add default dag definition dir
    dag_dirs = [_DAG_DEFINITION_DIR]
    if param.awel_dirs:
        dag_dirs += param.awel_dirs.strip().split(",")
    dag_dirs = [x.strip() for x in dag_dirs]

    initialize_awel(system_app, dag_dirs)
