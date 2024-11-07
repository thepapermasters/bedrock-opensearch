import json
from unittest.mock import MagicMock, patch


@patch('boto3.client')
def test_rekognition_batch_job(mock_boto_client):
    rekognition_mock = MagicMock()
    sqs_mock = MagicMock()

    # Simulate Rekognition response
    rekognition_mock.start_label_detection.return_value = {'JobId': 'test-job-id'}
    rekognition_mock.get_label_detection.return_value = {'Labels': [{'Name': 'TestLabel', 'Confidence': 99.9}]}

    # Simulate SQS message response
    sqs_mock.receive_message.return_value = {
        'Messages': [{
            'Body': json.dumps({
                'Message': json.dumps({
                    'JobId': 'test-job-id',
                    'Status': 'SUCCEEDED'
                })
            })
        }]
    }

    # Replace boto3 clients with mocks
    mock_boto_client.side_effect = [rekognition_mock, sqs_mock]

    # Call the actual function to test it with mocks
    test_rekognition_batch_job()

    # Validate Rekognition job status
    rekognition_mock.start_label_detection.assert_called_once()
    sqs_mock.receive_message.assert_called()
    rekognition_mock.get_label_detection.assert_called_once()
