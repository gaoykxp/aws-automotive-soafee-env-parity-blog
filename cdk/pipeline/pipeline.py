# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_codecommit as codecommit
import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_codepipeline_actions as codepipeline_actions
import os

class CdkPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        name = "yolo-v6-application"

        # ECR repositories
        container_repository = ecr.Repository(
            scope=self,
            id=f"{name}-container",
            repository_name=f"{name}"
        )
        
        container_repository.apply_removal_policy(aws_cdk.core.RemovalPolicy.DESTROY)
        
        # Repo for Application
        codecommit_repo = codecommit.Repository(
            scope=self, 
            id=f"{name}-container-git",
            repository_name=f"{name}",
            description=f"YOLO V6 Application code"
        )

        pipeline = codepipeline.Pipeline(
            scope=self, 
            id=f"{name}-container--pipeline",
            pipeline_name=f"{name}"
        )

        source_output = codepipeline.Artifact()
        docker_output_arm64 = codepipeline.Artifact("ARM64_BuildOutput")
        manifest_output = codepipeline.Artifact("ManifestOutput")

        buildspec_arm64 = codebuild.BuildSpec.from_source_filename("buildspec.yml")

        docker_build_arm64 = codebuild.PipelineProject(
            scope=self,
            id=f"DockerBuild_ARM64",
            environment=dict(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM,
                privileged=True),
            environment_variables={
                'REPO_ECR': codebuild.BuildEnvironmentVariable(
                    value=container_repository.repository_uri),
            },
            build_spec=buildspec_arm64
        )

        container_repository.grant_pull_push(docker_build_arm64)

        docker_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage"],
            resources=[f"arn:{core.Stack.of(self).partition}:ecr:{core.Stack.of(self).region}:{core.Stack.of(self).account}:repository/*"],))
       
        # build project for greengrass deploy to EC2
        greengrass_ec2_output_arm64 = codepipeline.Artifact("gg_ec2_ARM64_BuildOutput")
        gg_ec2_buildspec_arm64 = codebuild.BuildSpec.from_source_filename("greengrassbuildEC2spec.yml")
        gg_ec2_deploy_build_arm64 = codebuild.PipelineProject(
            scope=self,
            id=f"GreengrassBuild_ARM64",
            environment=dict(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM,
                privileged=True),
            build_spec=gg_ec2_buildspec_arm64
        )
        gg_ec2_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["greengrass:CreateComponentVersion"],
            resources=[f"arn:{core.Stack.of(self).partition}:greengrass:{core.Stack.of(self).region}:{core.Stack.of(self).account}:components:*"],))
            
        gg_ec2_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["greengrass:CreateDeployment"],
            resources=[f"arn:{core.Stack.of(self).partition}:greengrass:{core.Stack.of(self).region}:{core.Stack.of(self).account}:deployments"],))       

        gg_ec2_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:DescribeThingGroup", "iot:DescribeJob","iot:CreateJob"],
            resources=[f"arn:{core.Stack.of(self).partition}:iot:{core.Stack.of(self).region}:{core.Stack.of(self).account}:thinggroup/*"],))       

        gg_ec2_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:CreateJob","iot:DescribeJob","iot:CancelJob"],
            resources=[f"arn:{core.Stack.of(self).partition}:iot:{core.Stack.of(self).region}:{core.Stack.of(self).account}:job/*"],))       

        # build project for greengrass deploy to Edge
        greengrass_edge_output_arm64 = codepipeline.Artifact("gg_edge_ARM64_BuildOutput")
        gg_edge_buildspec_arm64 = codebuild.BuildSpec.from_source_filename("greengrassbuildedgespec.yml")
        gg_edge_deploy_build_arm64 = codebuild.PipelineProject(
            scope=self,
            id=f"GreengrassEdgeBuild_ARM64",
            environment=dict(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM,
                privileged=True),
            build_spec=gg_edge_buildspec_arm64
        )
        gg_edge_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["greengrass:CreateComponentVersion"],
            resources=[f"arn:{core.Stack.of(self).partition}:greengrass:{core.Stack.of(self).region}:{core.Stack.of(self).account}:components:*"],))
            
        gg_edge_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["greengrass:CreateDeployment"],
            resources=[f"arn:{core.Stack.of(self).partition}:greengrass:{core.Stack.of(self).region}:{core.Stack.of(self).account}:deployments"],))       

        gg_edge_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:DescribeThingGroup", "iot:DescribeJob","iot:CreateJob"],
            resources=[f"arn:{core.Stack.of(self).partition}:iot:{core.Stack.of(self).region}:{core.Stack.of(self).account}:thinggroup/*"],))       

        gg_edge_deploy_build_arm64.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["iot:CreateJob","iot:DescribeJob","iot:CancelJob"],
            resources=[f"arn:{core.Stack.of(self).partition}:iot:{core.Stack.of(self).region}:{core.Stack.of(self).account}:job/*"],))    

        # Stages in CodePipeline   
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit_Source",
            repository=codecommit_repo,
            output=source_output,
            branch="master"
        )

        # Stages in CodePipeline
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # Stages in CodePipeline
        pipeline.add_stage(
            stage_name="DockerBuild",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name=f"DockerBuild_ARM64",
                    project=docker_build_arm64,
                    input=source_output,
                    outputs=[docker_output_arm64])
            ]
        )

        # Manual approval greengreass deploy to EC2  Stages in CodePipeline
        pipeline.add_stage(
            stage_name="Manual-approval-Greengrass-Deploy-EC2",
            actions=[
                codepipeline_actions.ManualApprovalAction(
                    action_name=f"Manual-approval-Greengrass-Deploy-EC2")
            ]
        )
        # greengreass deploy to EC2 build Stages in CodePipeline

        pipeline.add_stage(
            stage_name="Greengrass-Deploy-EC2",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name=f"Greengrass_Deploy_To_EC2_Env",
                    project=gg_ec2_deploy_build_arm64,
                    input=source_output,
                    outputs=[greengrass_ec2_output_arm64])
            ]
        )

        # Manual approval greengreass deploy to Edge  Stages in CodePipeline
        pipeline.add_stage(
            stage_name="Manual-approval-Greengrass-Deploy-Edge",
            actions=[
                codepipeline_actions.ManualApprovalAction(
                    action_name=f"Manual-approval-Greengrass-Deploy-Edge")
            ]
        )

        # greengreass deploy to Edge build Stages in CodePipeline
        pipeline.add_stage(
            stage_name="Greengrass-Deploy-Edge",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name=f"Greengrass_Deploy_To_Edge_Env",
                    project=gg_edge_deploy_build_arm64,
                    input=source_output,
                    outputs=[greengrass_edge_output_arm64])
            ]
        )

        # Outputs
        core.CfnOutput(
            scope=self,
            id="application_repository",
            value=codecommit_repo.repository_clone_url_http
        )
