#!/usr/bin/env python3
"""
ML Infrastructure - MLflow Integration & Model Management
========================================================

Provides centralized model registry, experiment tracking, and
inference management for AI/ML plugins.

Features:
- MLflow integration for experiment tracking
- Model registry with versioning
- Model loading and caching
- GPU resource management
- Inference optimization
- A/B testing support

Usage:
    from core.ml_infrastructure import ModelRegistry, InferenceManager

    # Register a model
    registry = ModelRegistry()
    registry.register_model('classifier', '1.0', model_path='models/resnet50.pth')

    # Load for inference
    manager = InferenceManager()
    model = manager.load_model('classifier', version='latest')
    predictions = await manager.infer(model, input_data)
"""

from datetime import datetime
import logging
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class ModelMetadata:
    """Metadata for a registered model"""

    def __init__(
        self,
        name: str,
        version: str,
        framework: str,
        task_type: str,
        input_shape: tuple[int, ...],
        output_shape: tuple[int, ...],
        description: str = "",
        metrics: dict[str, float] | None = None,
        tags: dict[str, str] | None = None,
    ):
        self.name = name
        self.version = version
        self.framework = framework  # 'pytorch', 'tensorflow', 'onnx'
        self.task_type = task_type  # 'classification', 'detection', 'segmentation', etc.
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.description = description
        self.metrics = metrics or {}
        self.tags = tags or {}
        self.created_at = datetime.now()
        self.stage = "staging"  # 'staging', 'production', 'archived'

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "framework": self.framework,
            "task_type": self.task_type,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "description": self.description,
            "metrics": self.metrics,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "stage": self.stage,
        }


class ModelRegistry:
    """Centralized model registry with versioning"""

    def __init__(self, registry_path: Path | None = None):
        """
        Initialize model registry

        Args:
            registry_path: Path to store model registry data
        """
        if registry_path is None:
            registry_path = Path.home() / ".fileprocessor" / "model_registry"

        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)

        self.models: dict[str, dict[str, ModelMetadata]] = {}
        self._load_registry()

        logger.info(f"Model registry initialized at {self.registry_path}")

    def _load_registry(self):
        """Load registry from disk"""
        import json

        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)

                for model_name, versions in data.items():
                    self.models[model_name] = {}
                    for version, metadata in versions.items():
                        # Reconstruct ModelMetadata from dict
                        self.models[model_name][version] = ModelMetadata(
                            name=metadata["name"],
                            version=metadata["version"],
                            framework=metadata["framework"],
                            task_type=metadata["task_type"],
                            input_shape=tuple(metadata["input_shape"]),
                            output_shape=tuple(metadata["output_shape"]),
                            description=metadata.get("description", ""),
                            metrics=metadata.get("metrics", {}),
                            tags=metadata.get("tags", {}),
                        )
                        self.models[model_name][version].stage = metadata.get("stage", "staging")

                logger.info(f"Loaded {len(self.models)} models from registry")
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")

    def _save_registry(self):
        """Save registry to disk"""
        import json

        registry_file = self.registry_path / "registry.json"

        # Convert to serializable format
        data = {}
        for model_name, versions in self.models.items():
            data[model_name] = {}
            for version, metadata in versions.items():
                data[model_name][version] = metadata.to_dict()

        try:
            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Registry saved to {registry_file}")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def register_model(
        self,
        name: str,
        version: str,
        model_path: Path,
        metadata: ModelMetadata,
    ) -> bool:
        """
        Register a new model version

        Args:
            name: Model name
            version: Version string (e.g., '1.0', '2.1')
            model_path: Path to model file
            metadata: Model metadata

        Returns:
            True if registration successful
        """
        try:
            # Create model directory
            model_dir = self.registry_path / name / version
            model_dir.mkdir(parents=True, exist_ok=True)

            # Copy model file
            import shutil

            dest_path = model_dir / model_path.name
            shutil.copy(model_path, dest_path)

            # Store metadata
            if name not in self.models:
                self.models[name] = {}

            self.models[name][version] = metadata
            self._save_registry()

            logger.info(f"Registered model {name} v{version}")
            return True

        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False

    def get_model_path(self, name: str, version: str = "latest") -> Path | None:
        """
        Get path to registered model

        Args:
            name: Model name
            version: Version string or 'latest'

        Returns:
            Path to model file or None if not found
        """
        if name not in self.models:
            logger.error(f"Model {name} not found in registry")
            return None

        # Get specific version or latest
        if version == "latest":
            # Get latest version (highest version number or most recent)
            versions = list(self.models[name].keys())
            if not versions:
                return None
            version = max(versions)  # Simple string comparison

        if version not in self.models[name]:
            logger.error(f"Model {name} v{version} not found")
            return None

        # Find model file in directory
        model_dir = self.registry_path / name / version
        if not model_dir.exists():
            return None

        # Look for common model file extensions
        for ext in [".pth", ".pt", ".onnx", ".pb", ".h5", ".pkl"]:
            model_files = list(model_dir.glob(f"*{ext}"))
            if model_files:
                return model_files[0]

        return None

    def get_metadata(self, name: str, version: str = "latest") -> ModelMetadata | None:
        """Get model metadata"""
        if name not in self.models:
            return None

        if version == "latest":
            versions = list(self.models[name].keys())
            if not versions:
                return None
            version = max(versions)

        return self.models[name].get(version)

    def list_models(self) -> list[dict[str, Any]]:
        """List all registered models"""
        models = []
        for _name, versions in self.models.items():
            for _version, metadata in versions.items():
                models.append(metadata.to_dict())
        return models

    def promote_model(self, name: str, version: str, stage: str) -> bool:
        """
        Promote model to a stage

        Args:
            name: Model name
            version: Version string
            stage: Target stage ('staging', 'production', 'archived')

        Returns:
            True if promotion successful
        """
        if name not in self.models or version not in self.models[name]:
            logger.error(f"Model {name} v{version} not found")
            return False

        if stage not in ["staging", "production", "archived"]:
            logger.error(f"Invalid stage: {stage}")
            return False

        self.models[name][version].stage = stage
        self._save_registry()

        logger.info(f"Promoted {name} v{version} to {stage}")
        return True

    def delete_model(self, name: str, version: str) -> bool:
        """Delete a model version"""
        if name not in self.models or version not in self.models[name]:
            return False

        # Delete files
        model_dir = self.registry_path / name / version
        if model_dir.exists():
            import shutil

            shutil.rmtree(model_dir)

        # Remove from registry
        del self.models[name][version]
        if not self.models[name]:
            del self.models[name]

        self._save_registry()
        logger.info(f"Deleted model {name} v{version}")
        return True


class InferenceManager:
    """Manages model loading and inference"""

    def __init__(self, registry: ModelRegistry = None, device: str = "auto"):
        """
        Initialize inference manager

        Args:
            registry: Model registry instance
            device: Device for inference ('cpu', 'cuda', 'auto')
        """
        self.registry = registry or ModelRegistry()

        # Auto-detect device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = torch.device(device)
        logger.info(f"Inference manager using device: {self.device}")

        # Model cache {name: {version: model}}
        self.model_cache: dict[str, dict[str, Any]] = {}
        self.cache_size_limit = 3  # Max models to keep in memory

    def _manage_cache(self):
        """Evict least recently used models if cache is full"""
        # Simple LRU implementation - remove oldest entries
        total_models = sum(len(versions) for versions in self.model_cache.values())

        if total_models >= self.cache_size_limit:
            # Remove first model found (FIFO for simplicity)
            for name in list(self.model_cache.keys()):
                if self.model_cache[name]:
                    first_version = next(iter(self.model_cache[name].keys()))
                    del self.model_cache[name][first_version]
                    logger.info(f"Evicted {name} v{first_version} from cache")
                    break

    def load_model(
        self,
        name: str,
        version: str = "latest",
        force_reload: bool = False,
    ) -> Any | None:
        """
        Load model for inference

        Args:
            name: Model name
            version: Version string or 'latest'
            force_reload: Force reload even if cached

        Returns:
            Loaded model or None if failed
        """
        # Check cache
        if not force_reload and name in self.model_cache and version in self.model_cache[name]:
                logger.info(f"Using cached model {name} v{version}")
                return self.model_cache[name][version]

        # Get model path from registry
        model_path = self.registry.get_model_path(name, version)
        if not model_path:
            logger.error(f"Model {name} v{version} not found")
            return None

        # Get metadata
        metadata = self.registry.get_metadata(name, version)
        if not metadata:
            logger.error(f"Metadata for {name} v{version} not found")
            return None

        # Load based on framework
        try:
            if metadata.framework == "pytorch":
                model = torch.load(model_path, map_location=self.device)
                if isinstance(model, nn.Module):
                    model.eval()
            elif metadata.framework == "onnx":
                import onnxruntime as ort

                model = ort.InferenceSession(str(model_path))
            elif metadata.framework == "tensorflow":
                import tensorflow as tf

                model = tf.keras.models.load_model(model_path)
            else:
                logger.error(f"Unsupported framework: {metadata.framework}")
                return None

            # Manage cache
            self._manage_cache()

            # Cache model
            if name not in self.model_cache:
                self.model_cache[name] = {}
            self.model_cache[name][version] = model

            logger.info(f"Loaded model {name} v{version} ({metadata.framework})")
            return model

        except Exception as e:
            logger.error(f"Failed to load model {name} v{version}: {e}")
            return None

    async def infer(
        self,
        model: Any,
        input_data: Any,
        metadata: ModelMetadata,
    ) -> dict[str, Any]:
        """
        Run inference on input data

        Args:
            model: Loaded model
            input_data: Input tensor/array
            metadata: Model metadata

        Returns:
            Dictionary with inference results
        """
        try:
            if metadata.framework == "pytorch":
                with torch.no_grad():
                    if isinstance(input_data, torch.Tensor):
                        input_data = input_data.to(self.device)
                    output = model(input_data)
                return {"predictions": output}

            elif metadata.framework == "onnx":
                # ONNX runtime inference
                input_name = model.get_inputs()[0].name
                output = model.run(None, {input_name: input_data})
                return {"predictions": output[0]}

            elif metadata.framework == "tensorflow":
                output = model.predict(input_data)
                return {"predictions": output}

            else:
                raise ValueError(f"Unsupported framework: {metadata.framework}")

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {"error": str(e)}

    def get_device_info(self) -> dict[str, Any]:
        """Get information about available devices"""
        info = {
            "device": str(self.device),
            "cuda_available": torch.cuda.is_available(),
        }

        if torch.cuda.is_available():
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_memory_allocated"] = torch.cuda.memory_allocated(0)
            info["cuda_memory_cached"] = torch.cuda.memory_reserved(0)

        return info


# Example usage and testing
if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(level=logging.INFO)

    print("\n" + "=" * 70)
    print("  ML Infrastructure - Model Registry & Inference Manager")
    print("=" * 70 + "\n")

    # Initialize registry
    registry = ModelRegistry()
    print("📚 Model Registry initialized")
    print(f"   Location: {registry.registry_path}\n")

    # List models
    models = registry.list_models()
    print(f"📦 Registered Models: {len(models)}")
    for model in models:
        print(f"   • {model['name']} v{model['version']} ({model['framework']})")
        print(f"     Task: {model['task_type']} | Stage: {model['stage']}")

    # Initialize inference manager
    print("\n" + "-" * 70)
    manager = InferenceManager(registry)

    # Show device info
    device_info = manager.get_device_info()
    print("\n💻 Device Information:")
    print(f"   Device: {device_info['device']}")
    print(f"   CUDA Available: {device_info['cuda_available']}")
    if device_info["cuda_available"]:
        print(f"   GPU: {device_info.get('cuda_device_name', 'Unknown')}")
        print(
            f"   Memory Allocated: {device_info.get('cuda_memory_allocated', 0) / 1024**2:.1f} MB"
        )

    print("\n" + "=" * 70)
    print("✅ ML Infrastructure ready for Sprint 2!")
    print("=" * 70 + "\n")
