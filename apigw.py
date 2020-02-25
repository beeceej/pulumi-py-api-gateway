import pulumi
from pulumi_aws import apigateway


class APIGateway:
    def __init__(self, name: str, _lambda):
        self.name = name
        self._lambda = _lambda

    def _endpoint(self, rest_api, path_part):
        _name = f"{self.name}-{path_part}"
        endpoint = apigateway.Resource(
            _name,
            opts=pulumi.ResourceOptions(depends_on=[rest_api]),
            parent_id=rest_api.root_resource_id,
            path_part=path_part,
            rest_api=rest_api.id,
        )
        method = apigateway.Method(
            _name,
            opts=pulumi.ResourceOptions(depends_on=[rest_api, endpoint]),
            http_method="GET",
            rest_api=rest_api.id,
            resource_id=endpoint.id,
            authorization="NONE",
        )
        integration = apigateway.Integration(
            _name,
            opts=pulumi.ResourceOptions(depends_on=[rest_api, endpoint, method]),
            integration_http_method="POST",
            http_method=method.http_method,
            type="AWS",
            uri=self._lambda.invoke_arn,
            resource_id=endpoint.id,
            rest_api=rest_api.id,
        )
        method_response = apigateway.MethodResponse(
            _name,
            opts=pulumi.ResourceOptions(depends_on=[rest_api, endpoint, method]),
            http_method=method.http_method,
            rest_api=rest_api.id,
            resource_id=endpoint.id,
            status_code=200,
        )
        integration_response = apigateway.IntegrationResponse(
            _name,
            opts=pulumi.ResourceOptions(
                depends_on=[rest_api, endpoint, method, integration]
            ),
            http_method=method.http_method,
            rest_api=rest_api.id,
            resource_id=endpoint.id,
            status_code=200,
        )
        responses = [method_response, integration_response]
        return endpoint, [method, integration] + responses

    def build(self):
        rest_api = apigateway.RestApi(
            self.name, opts=pulumi.ResourceOptions(depends_on=[self._lambda])
        )

        hello, hello_components = self._endpoint(rest_api, "hello")
        bonjour, bonjour_components = self._endpoint(rest_api, "bonjour")
        components = hello_components + bonjour_components
        deployment = apigateway.Deployment(
            self.name,
            opts=pulumi.ResourceOptions(
                depends_on=[rest_api, hello, bonjour] + components
            ),
            rest_api=rest_api.id,
        )
        stage = apigateway.Stage(
            self.name,
            opts=pulumi.ResourceOptions(depends_on=[deployment]),
            deployment=deployment.id,
            rest_api=rest_api.id,
            stage_name="dev",
        )
        return rest_api
