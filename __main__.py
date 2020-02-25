import pulumi
import iam
import apigw
from pulumi_aws import lambda_


def main():
    hello_world_lambda = lambda_.Function(
        "hello_world",
        runtime="python3.7",
        role=iam.lambda_role.arn,
        description="pulumi lambda hello world",
        handler="main.handler",
        code=pulumi.AssetArchive({".": pulumi.FileArchive("./lambda")}),
    )
    hello_world_api = apigw.APIGateway("hello_world", hello_world_lambda)
    hello_world_api = hello_world_api.build()
    lambda_.Permission(
        "hello_world",
        function=hello_world_lambda.name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        source_arn=hello_world_api.execution_arn.apply(lambda s: f"{s}/*/*"),
    )


if __name__ == "__main__":
    main()
