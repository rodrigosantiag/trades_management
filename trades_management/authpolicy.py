# From AWS Labs
# Apache License 2.0
# https://github.com/awslabs/aws-apigateway-lambda-authorizer-blueprints

import re


class Effect:  # pragma: no cover
    ALLOW = "Allow"
    DENY = "Deny"


class HttpVerb:  # pragma: no cover
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    ALL = "*"


class AuthPolicy(object):  # pragma: no cover
    awsAccountId = ""
    principalId = ""
    version = "2012-10-17"
    pathRegex = "^[/.a-zA-Z0-9-\\*]+$"

    allowMethods = []
    denyMethods = []

    restApiId = "*"
    region = "*"
    stage = "*"
    context = {}

    def __init__(self, principal, methodarn):
        tmp = methodarn.split(":")
        apiGatewayArnTmp = tmp[5].split("/")
        awsAccountId = tmp[4]

        self.restApiId = apiGatewayArnTmp[0]
        self.region = tmp[3]
        self.stage = apiGatewayArnTmp[1]

        self.awsAccountId = awsAccountId
        self.principalId = principal
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):
        if verb != "*" and not hasattr(HttpVerb, verb):
            raise NameError("Invalid HTTP verb " + verb + ". Allowed verbs in HttpVerb class")
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError(
                f"Invalid resource path: {resource}. Path should match {self.pathRegex}"
            )

        if resource[:1] == "/":
            resource = resource[1:]

        resourceArn = "arn:aws:execute-api:{}:{}:{}/{}/{}/{}".format(
            self.region, self.awsAccountId, self.restApiId, self.stage, verb, resource
        )

        if effect == Effect.ALLOW:
            self.allowMethods.append({"resourceArn": resourceArn, "conditions": conditions})
        elif effect == Effect.DENY:
            self.denyMethods.append({"resourceArn": resourceArn, "conditions": conditions})

    def _getEmptyStatement(self, effect):
        statement = {
            "Action": "execute-api:Invoke",
            "Effect": effect[:1].upper() + effect[1:].lower(),
            "Resource": [],
        }

        return statement

    def _getStatementForEffect(self, effect, methods):
        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod["conditions"] is None or len(curMethod["conditions"]) == 0:
                    statement["Resource"].append(curMethod["resourceArn"])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement["Resource"].append(curMethod["resourceArn"])
                    conditionalStatement["Condition"] = curMethod["conditions"]
                    statements.append(conditionalStatement)

            statements.append(statement)

        return statements

    def allowAllMethods(self):
        self._addMethod(Effect.ALLOW, HttpVerb.ALL, "*", [])

    def denyAllMethods(self):
        self._addMethod(Effect.DENY, HttpVerb.ALL, "*", [])

    def allowMethod(self, verb, resource):
        self._addMethod(Effect.ALLOW, verb, resource, [])

    def denyMethod(self, verb, resource):
        self._addMethod("Deny", verb, resource, [])

    def allowMethodWithConditions(self, verb, resource, conditions):
        self._addMethod(Effect.ALLOW, verb, resource, conditions)

    def denyMethodWithConditions(self, verb, resource, conditions):
        self._addMethod(Effect.DENY, verb, resource, conditions)

    def build(self):
        if (self.allowMethods is None or len(self.allowMethods) == 0) and (
            self.denyMethods is None or len(self.denyMethods) == 0
        ):
            raise NameError("No statements defined for the policy")

        policy = {
            "principalId": self.principalId,
            "policyDocument": {"Version": self.version, "Statement": []},
            "context": self.context,
        }

        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect(Effect.ALLOW, self.allowMethods)
        )
        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect(Effect.DENY, self.denyMethods)
        )

        return policy
