from typing import Mapping, List, Optional

from grpclib.client import Channel

from viam import logging
from viam.proto.app.mltraining import (
    CancelTrainingJobRequest,
    GetTrainingJobRequest,
    GetTrainingJobResponse,
    ListTrainingJobsRequest,
    ListTrainingJobsResponse,
    MLTrainingServiceStub,
    ModelType,
    SubmitTrainingJobRequest,
    SubmitTrainingJobResponse,
    TrainingStatus,
    TrainingJobMetadata,
)
from viam.proto.app.data import Filter

LOGGER = logging.getLogger(__name__)


class MLTrainingClient:
    """gRPC client for working with ML training jobs.

    Constructor is used by `ViamClient` to instantiate relevant service stubs.
    Calls to `MLTrainingClient` methods should be made through `ViamClient`.
    """

    def __init__(self, channel: Channel, metadata: Mapping[str, str]):
        """Create a `MLTrainingClient` that maintains a connection to app.

        Args:
            channel (grpclib.client.Channel): Connection to app.
            metadata (Mapping[str, str]): Required authorization token to send requests to app.
        """
        self._metadata = metadata
        self._ml_training_client = MLTrainingServiceStub(channel)
        self._channel = channel

    async def submit_training_job(
        self,
        org_id: str,
        model_name: str,
        model_version: str,
        model_type: ModelType,
        tags: List[str],
        filter: Optional[Filter] = None,
    ) -> str:
        """Submits a training job to be processed by the training job manager.

        Args:
            org_id (str): the ID of the organization whose data will be used for training.
            model_name (str): the training model name.
            model_version (str): the training model version.
            model_type (viam.proto.app.mltraining.ModelType): the training model type.
            tags (List[str]): list of tags to apply to the training model output.
            filter (Optional[viam.proto.app.data.Filter]): `Filter` specifying which data to include when training.
            If unspecified, all data will be included.

        Returns:
            str: the id assigned to the training job.
        """

        request = SubmitTrainingJobRequest(
            organization_id=org_id,
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            tags=tags,
            filter=filter,
        )
        response: SubmitTrainingJobResponse = await self._ml_training_client.SubmitTrainingJob(request, metadata=self._metadata)

        return response.id

    async def get_training_job(self, id: str) -> TrainingJobMetadata:
        """Gets training job data.

        Args:
            id (str): id of the requested training job.

        Returns:
            viam.proto.app.mltraining.TrainingJobMetadata: training job data.
        """

        request = GetTrainingJobRequest(id=id)
        response: GetTrainingJobResponse = await self._ml_training_client.GetTrainingJob(request, metadata=self._metadata)

        return response.metadata

    async def list_training_jobs(self, org_id: str, training_status: Optional[TrainingStatus.ValueType]) -> List[TrainingJobMetadata]:
        """Returns training job data for all jobs within an org.

        Args:
            org_id (str): the id of the org to request training job data from.
            training_status (Optional[TrainingStatus]): status of training jobs to filter the list by.
            If unspecified, all training jobs will be returned.

        Returns:
            List[viam.proto.app.mltraining.TrainingJobMetadata]: a list of training job data.
        """

        training_status = training_status if training_status else TrainingStatus.TRAINING_STATUS_UNSPECIFIED
        request = ListTrainingJobsRequest(organization_id=org_id, status=training_status)
        response: ListTrainingJobsResponse = await self._ml_training_client.ListTrainingJobs(request, metadata=self._metadata)

        return list(response.jobs)

    async def cancel_training_job(self, id: str) -> None:
        """Cancels the specified training job.

        Args:
            id (str): the id of the job to be canceled.
        """

        request = CancelTrainingJobRequest(id=id)
        await self._ml_training_client.CancelTrainingJob(request, metadata=self._metadata)
