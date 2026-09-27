import shutil
import subprocess
from pathlib import Path

class DockerError(Exception):
    """Base Docker exception."""

class DockerNotInstalledError(DockerError):
    """Docker executable not found."""

class DockerNotRunningError(DockerError):
    """Docker daemon not running."""


class YarrrmlError(Exception):
    """YARRRML conversion error."""

class RMLMapperError(Exception):
    """RMLMapper execution error."""

class YarrrmlHandler:
    """
    Utility class for executing YARRRML and RMLMapper Docker containers.
    """

    YARRRML_IMAGE = "yarrrml-parser:latest" #"rmlio/yarrrml-parser:1.10.0"
    RMLMAPPER_IMAGE = "rmlio/rmlmapper-java:v7.3.3"

    @staticmethod
    def _check_docker() -> None:
        """Verify Docker is installed and running."""

        if shutil.which("docker") is None:
            raise DockerNotInstalledError(
                "Docker executable not found. Please install Docker."
            )

        try:
            subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise DockerNotRunningError(
                "Docker daemon is not running."
            ) from e

    @staticmethod
    def _ensure_image(image: str) -> None:
        """Ensure a Docker image exists locally."""

        result = subprocess.run(
            ["docker", "image", "inspect", image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if result.returncode != 0:
            try:
                subprocess.run(
                    ["docker", "pull", image],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                raise DockerError(
                    f"Unable to pull Docker image '{image}'."
                ) from e

    @staticmethod
    def _validate_directory(directory: str | Path) -> Path:
        """Validate and resolve the working directory."""

        path = Path(directory).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {path}"
            )

        if not path.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {path}"
            )

        return path

    @staticmethod
    def yarrrml_to_rml(
        working_dir: str | Path,
        input_file: str,
        output_file: str = "rules.rml.ttl",
    ) -> Path:
        """
        Convert YARRRML to RML.
        """
        YarrrmlHandler._check_docker()
        YarrrmlHandler._ensure_image(
            YarrrmlHandler.YARRRML_IMAGE
        )

        workdir = YarrrmlHandler._validate_directory(
            working_dir
        )

        input_path = workdir / input_file

        if not input_path.exists():
            raise FileNotFoundError(
                f"Input file not found: {input_path}"
            )

        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{workdir}:/data",
            YarrrmlHandler.YARRRML_IMAGE,
            "-i",
            f"/data/{input_file}",
            "-o",
            f"/data/{output_file}",
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=300,
            )
        except subprocess.CalledProcessError as e:
            raise YarrrmlError(
                f"YARRRML conversion failed.\n{e.stderr}"
            ) from e

        output_path = workdir / output_file
 
        if not output_path.exists():
            raise YarrrmlError(
                f"Output file not created: {output_path}"
            )
        return output_path

    @staticmethod
    def execute_mapping(
        working_dir: str | Path,
        mapping_file: str = "rules.rml.ttl",
    ) -> subprocess.CompletedProcess:
        """
        Execute RMLMapper.
        """

        YarrrmlHandler._check_docker()
        YarrrmlHandler._ensure_image(
            YarrrmlHandler.RMLMAPPER_IMAGE
        )

        workdir = YarrrmlHandler._validate_directory(
            working_dir
        )

        mapping_path = workdir / mapping_file

        if not mapping_path.exists():
            raise FileNotFoundError(
                f"Mapping file not found: {mapping_path}"
            )

        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{workdir}:/data",
            YarrrmlHandler.RMLMAPPER_IMAGE,
            "-m",
            f"/data/{mapping_file}"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=600,
            )

            return result

        except subprocess.CalledProcessError as e:
            raise RMLMapperError(
                f"RMLMapper execution failed.\n{e.stderr}"
            ) from e

    @staticmethod
    def run_pipeline(
        working_dir: str | Path,
        yarrrml_file: str,
        rml_file: str = "rules.rml.ttl",
    ) -> subprocess.CompletedProcess:
        """
        Execute the complete pipeline:

        YARRRML -> RML -> RDF
        """

        YarrrmlHandler.yarrrml_to_rml(
            working_dir=working_dir,
            input_file=yarrrml_file,
            output_file=rml_file,
        )

        return YarrrmlHandler.execute_mapping(
            working_dir=working_dir,
            mapping_file=rml_file,
        )
